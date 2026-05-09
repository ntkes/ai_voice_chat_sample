from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class HistoryConfig:
    max_messages: int


@dataclass(frozen=True)
class SpeechRecognitionConfig:
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


@dataclass(frozen=True)
class AppConfig:
    log_file: Path
    history: HistoryConfig
    speech_recognition: SpeechRecognitionConfig
    ai: AIConfig


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
    speech_config = SpeechRecognitionConfig(
        language=str(speech["language"]),
        ambient_duration=float(speech["ambient_duration"]),
        listen_timeout=float(speech["listen_timeout"]),
        phrase_time_limit=float(speech["phrase_time_limit"]),
        exit_phrases={str(value).strip().lower() for value in speech["exit_phrases"]},
    )

    ai = raw["ai"]
    ai_config = AIConfig(
        api_url=str(ai["api_url"]),
        model_name=str(ai["model_name"]),
        temperature=float(ai["temperature"]),
        timeout_seconds=int(ai["timeout_seconds"]),
        system_prompt=str(ai["system_prompt"]),
    )

    # Keep paths relative to the config file location, not process CWD.
    log_file = (config_path.parent / str(raw["log_file"]))

    return AppConfig(
        log_file=log_file,
        history=history,
        speech_recognition=speech_config,
        ai=ai_config,
    )
