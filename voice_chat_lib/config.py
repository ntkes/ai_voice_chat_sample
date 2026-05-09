from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class HistoryConfig:
    max_messages: int


@dataclass(frozen=True)
class SpeechRecognitionConfig:
    engine: str
    language: str
    ambient_duration: float
    listen_timeout: float
    phrase_time_limit: float
    exit_phrases: set[str]


@dataclass(frozen=True)
class AIConfig:
    api_url: str
    model_name: str
    temperature: float
    timeout_seconds: int
    system_prompt: str
    voicevox_character_prompts: dict[int, str]


@dataclass(frozen=True)
class VoiceVoxConfig:
    base_url: str
    speaker: int
    timeout_seconds: int
    speed_scale: float
    pitch_scale: float
    intonation_scale: float
    volume_scale: float
    pre_phoneme_length: float
    post_phoneme_length: float


@dataclass(frozen=True)
class Pyttsx3Config:
    rate: int | None
    volume: float | None
    voice_name: str | None


@dataclass(frozen=True)
class PowerShellTTSConfig:
    rate: int
    volume: int


@dataclass(frozen=True)
class TTSConfig:
    provider: str
    fallback_providers: list[str]
    voicevox: VoiceVoxConfig
    pyttsx3: Pyttsx3Config
    powershell: PowerShellTTSConfig


@dataclass(frozen=True)
class AppConfig:
    log_file: Path
    history: HistoryConfig
    speech_recognition: SpeechRecognitionConfig
    ai: AIConfig
    tts: TTSConfig


def load_config(config_path: Path) -> AppConfig:
    # Resolve configuration once so relative paths (like log_file) are stable.
    config_path = config_path.resolve()

    with config_path.open("r", encoding="utf-8") as file:
        suffix = config_path.suffix.lower()
        if suffix in {".yaml", ".yml"}:
            raw = yaml.safe_load(file)
        else:
            raise ValueError(
                f"Unsupported config extension: {config_path.suffix}. "
                "Use .yaml or .yml"
            )

    history = HistoryConfig(max_messages=int(raw["history"]["max_messages"]))

    speech = raw["speech_recognition"]
    recognition_engine = str(speech.get("engine", "google")).strip().lower()
    if recognition_engine not in {"google", "sphinx"}:
        raise ValueError(
            "speech_recognition.engine must be one of: google, sphinx"
        )

    speech_config = SpeechRecognitionConfig(
        engine=recognition_engine,
        language=str(speech["language"]),
        ambient_duration=float(speech["ambient_duration"]),
        listen_timeout=float(speech["listen_timeout"]),
        phrase_time_limit=float(speech["phrase_time_limit"]),
        exit_phrases={str(value).strip().lower() for value in speech["exit_phrases"]},
    )

    ai = raw["ai"]
    voicevox_character_prompts_raw = ai.get("voicevox_character_prompts", {})
    voicevox_character_prompts: dict[int, str] = {}
    for key, value in voicevox_character_prompts_raw.items():
        voicevox_character_prompts[int(key)] = str(value)

    ai_config = AIConfig(
        api_url=str(ai["api_url"]),
        model_name=str(ai["model_name"]),
        temperature=float(ai["temperature"]),
        timeout_seconds=int(ai["timeout_seconds"]),
        system_prompt=str(ai["system_prompt"]),
        voicevox_character_prompts=voicevox_character_prompts,
    )

    tts = raw.get("tts", {})
    voicevox_raw = tts.get("voicevox", {})
    pyttsx3_raw = tts.get("pyttsx3", {})
    powershell_raw = tts.get("powershell", {})

    voicevox_config = VoiceVoxConfig(
        base_url=str(voicevox_raw.get("base_url", "http://127.0.0.1:50021")),
        speaker=int(voicevox_raw.get("speaker", 3)),
        timeout_seconds=int(voicevox_raw.get("timeout_seconds", 15)),
        speed_scale=float(voicevox_raw.get("speed_scale", 1.0)),
        pitch_scale=float(voicevox_raw.get("pitch_scale", 0.0)),
        intonation_scale=float(voicevox_raw.get("intonation_scale", 1.0)),
        volume_scale=float(voicevox_raw.get("volume_scale", 1.0)),
        pre_phoneme_length=float(voicevox_raw.get("pre_phoneme_length", 0.1)),
        post_phoneme_length=float(voicevox_raw.get("post_phoneme_length", 0.1)),
    )

    pyttsx3_config = Pyttsx3Config(
        rate=(None if pyttsx3_raw.get("rate") is None else int(pyttsx3_raw["rate"])),
        volume=(None if pyttsx3_raw.get("volume") is None else float(pyttsx3_raw["volume"])),
        voice_name=(None if pyttsx3_raw.get("voice_name") is None else str(pyttsx3_raw["voice_name"])),
    )

    powershell_config = PowerShellTTSConfig(
        rate=int(powershell_raw.get("rate", 0)),
        volume=int(powershell_raw.get("volume", 100)),
    )

    tts_config = TTSConfig(
        provider=str(tts.get("provider", "pyttsx3")).strip().lower(),
        fallback_providers=[str(value).strip().lower() for value in tts.get("fallback_providers", ["pyttsx3", "powershell"])],
        voicevox=voicevox_config,
        pyttsx3=pyttsx3_config,
        powershell=powershell_config,
    )

    # Keep paths relative to the config file location, not process CWD.
    log_file = (config_path.parent / str(raw["log_file"]))

    return AppConfig(
        log_file=log_file,
        history=history,
        speech_recognition=speech_config,
        ai=ai_config,
        tts=tts_config,
    )
