from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

import speech_recognition as sr


def append_line(file_path: Path, text: str) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("a", encoding="utf-8") as file:
        file.write(text + "\n")


def build_recognizer() -> sr.Recognizer:
    return sr.Recognizer()


def calibrate_microphone(
    recognizer: sr.Recognizer,
    source: sr.AudioSource,
    duration: float,
) -> None:
    recognizer.adjust_for_ambient_noise(source, duration=duration)


def capture_text(
    recognizer: sr.Recognizer,
    source: sr.AudioSource,
    language: str,
    timeout: Optional[float],
    phrase_time_limit: Optional[float],
) -> str:
    audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
    return recognizer.recognize_google(audio, language=language).strip()


def format_log_line(speaker: str, text: str) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"[{now}] {speaker}: {text}"
