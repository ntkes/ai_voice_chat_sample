from __future__ import annotations

import json
import subprocess
import urllib.parse
import urllib.request
import winsound

import pyttsx3

from voice_chat_lib.config import TTSConfig


def _escape_for_powershell(text: str) -> str:
    # Escape double quotes for interpolation in a PowerShell string.
    return text.replace("`", "``").replace('"', '`"')


def _speak_with_pyttsx3(text: str, tts_config: TTSConfig) -> None:
    engine = pyttsx3.init()

    if tts_config.pyttsx3.rate is not None:
        engine.setProperty("rate", tts_config.pyttsx3.rate)
    if tts_config.pyttsx3.volume is not None:
        engine.setProperty("volume", tts_config.pyttsx3.volume)

    if tts_config.pyttsx3.voice_name:
        target_name = tts_config.pyttsx3.voice_name.lower()
        for voice in engine.getProperty("voices"):
            if target_name in str(voice.name).lower():
                engine.setProperty("voice", voice.id)
                break

    engine.say(text)
    engine.runAndWait()


def _speak_with_powershell(text: str, tts_config: TTSConfig) -> None:
    escaped = _escape_for_powershell(text)
    ps_script = (
        "Add-Type -AssemblyName System.Speech; "
        "$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        f"$synth.Rate = {tts_config.powershell.rate}; "
        f"$synth.Volume = {tts_config.powershell.volume}; "
        f'$synth.Speak("{escaped}")'
    )
    subprocess.run(
        ["powershell", "-NoProfile", "-Command", ps_script],
        check=True,
    )


def _speak_with_voicevox(text: str, tts_config: TTSConfig) -> None:
    vv = tts_config.voicevox

    query_params = urllib.parse.urlencode({"text": text, "speaker": vv.speaker})
    audio_query_url = f"{vv.base_url.rstrip('/')}" + f"/audio_query?{query_params}"
    audio_query_request = urllib.request.Request(
        audio_query_url,
        method="POST",
        data=b"",
    )

    with urllib.request.urlopen(audio_query_request, timeout=vv.timeout_seconds) as response:
        query_json = response.read().decode("utf-8")

    query = json.loads(query_json)
    query["speedScale"] = vv.speed_scale
    query["pitchScale"] = vv.pitch_scale
    query["intonationScale"] = vv.intonation_scale
    query["volumeScale"] = vv.volume_scale
    query["prePhonemeLength"] = vv.pre_phoneme_length
    query["postPhonemeLength"] = vv.post_phoneme_length

    synthesis_params = urllib.parse.urlencode({"speaker": vv.speaker})
    synthesis_url = f"{vv.base_url.rstrip('/')}" + f"/synthesis?{synthesis_params}"
    synthesis_request = urllib.request.Request(
        synthesis_url,
        method="POST",
        data=json.dumps(query).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )

    with urllib.request.urlopen(synthesis_request, timeout=vv.timeout_seconds) as response:
        wav_bytes = response.read()

    winsound.PlaySound(wav_bytes, winsound.SND_MEMORY)


def _build_provider_order(tts_config: TTSConfig) -> list[str]:
    ordered = [tts_config.provider, *tts_config.fallback_providers]
    deduped: list[str] = []
    for provider in ordered:
        name = provider.strip().lower()
        if not name:
            continue
        if name not in deduped:
            deduped.append(name)
    return deduped


def speak_text(text: str, tts_config: TTSConfig) -> None:
    provider_order = _build_provider_order(tts_config)
    last_error: Exception | None = None

    for provider in provider_order:
        try:
            if provider == "voicevox":
                _speak_with_voicevox(text, tts_config)
                return
            if provider == "pyttsx3":
                _speak_with_pyttsx3(text, tts_config)
                return
            if provider == "powershell":
                _speak_with_powershell(text, tts_config)
                return
            raise ValueError(f"Unsupported tts provider: {provider}")
        except Exception as exc:
            last_error = exc

    raise RuntimeError("All TTS providers failed") from last_error
