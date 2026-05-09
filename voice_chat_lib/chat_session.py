from __future__ import annotations

from pathlib import Path

import speech_recognition as sr

from voice_chat_lib.ai_agent import request_chat_reply
from voice_chat_lib.config import AppConfig, load_config
from voice_chat_lib.mic_in import append_line, build_recognizer, calibrate_microphone, capture_text, format_log_line
from voice_chat_lib.speaker_out import speak_text


def should_exit(text: str, exit_phrases: set[str]) -> bool:
    return text.strip().lower() in exit_phrases


def trim_history(history: list[dict[str, str]], max_messages: int) -> list[dict[str, str]]:
    if len(history) <= max_messages:
        return history
    return history[-max_messages:]


def run_voice_chat(config_path: Path) -> None:
    config: AppConfig = load_config(config_path)
    recognizer = build_recognizer()
    history: list[dict[str, str]] = []

    print("音声チャットを開始します。終了するには設定の終了ワードを話してください。")

    try:
        with sr.Microphone() as source:
            print("周囲ノイズを調整中...")
            calibrate_microphone(
                recognizer,
                source,
                duration=config.speech_recognition.ambient_duration,
            )
            print("準備完了。話しかけてください。")

            while True:
                print("\nListening...")
                try:
                    # Capture a single utterance with timeout and phrase limits.
                    user_text = capture_text(
                        recognizer,
                        source,
                        language=config.speech_recognition.language,
                        timeout=config.speech_recognition.listen_timeout,
                        phrase_time_limit=config.speech_recognition.phrase_time_limit,
                    )
                except sr.WaitTimeoutError:
                    print("入力待機がタイムアウトしました。もう一度話してください。")
                    continue
                except sr.UnknownValueError:
                    print("音声を認識できませんでした。もう一度お願いします。")
                    continue
                except sr.RequestError as exc:
                    print(f"音声認識APIでエラー: {exc}")
                    break

                print(f"You: {user_text}")
                append_line(config.log_file, format_log_line("User", user_text))

                if should_exit(user_text, config.speech_recognition.exit_phrases):
                    print("終了コマンドを検出しました。会話を終了します。")
                    break

                try:
                    # Pass trimmed history so the model keeps short context.
                    reply = request_chat_reply(
                        user_text=user_text,
                        ai_config=config.ai,
                        history=history,
                    )
                except Exception as exc:
                    print(f"AI応答の取得に失敗しました: {exc}")
                    continue

                print(f"Assistant: {reply}")
                append_line(config.log_file, format_log_line("Assistant", reply))

                try:
                    speak_text(reply)
                except Exception as exc:
                    print(f"音声出力に失敗しました: {exc}")

                history.extend(
                    [
                        {"role": "user", "content": user_text},
                        {"role": "assistant", "content": reply},
                    ]
                )
                history = trim_history(history, config.history.max_messages)

    except OSError as exc:
        print(f"マイクを開けませんでした: {exc}")
