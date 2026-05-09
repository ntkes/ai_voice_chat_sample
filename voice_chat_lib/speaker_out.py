from __future__ import annotations

import subprocess

import pyttsx3


def _escape_for_powershell(text: str) -> str:
    # Escape double quotes for interpolation in a PowerShell string.
    return text.replace('"', '`"')


def speak_text(text: str) -> None:
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        return
    except Exception:
        escaped = _escape_for_powershell(text)
        ps_script = (
            "Add-Type -AssemblyName System.Speech; "
            "$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
            f'$synth.Speak("{escaped}")'
        )
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_script],
            check=True,
        )
