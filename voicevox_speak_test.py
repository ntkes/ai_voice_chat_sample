from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path
import sys

from voice_chat_lib.config import load_config
from voice_chat_lib.speaker_out import speak_text


# IDs fetched from VOICEVOX Engine /speakers API on this environment.
# - ずんだもん (ノーマル): 3
# - 春日部つむぎ (ノーマル): 8
# - 四国めたん: 2 (ノーマル), 0 (あまあま), 6 (ツンツン), 4 (セクシー), 36 (ささやき), 37 (ヒソヒソ)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="VOICEVOX playback test")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("chat_config.yaml"),
        help="Path to YAML config file",
    )
    parser.add_argument(
        "--text",
        default="VOICEVOXの再生テストです。",
        help="Text to speak",
    )
    parser.add_argument(
        "--speaker",
        type=int,
        default=None,
        help="VOICEVOX speaker style ID (e.g. 3:ずんだもん, 8:春日部つむぎ, 2:四国めたん)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    try:
        config = load_config(args.config)
        # Force VOICEVOX only for this test script.
        voicevox = config.tts.voicevox
        if args.speaker is not None:
            voicevox = replace(voicevox, speaker=args.speaker)
        tts = replace(
            config.tts,
            provider="voicevox",
            fallback_providers=[],
            voicevox=voicevox,
        )
        print("VOICEVOXで再生します...")
        speak_text(args.text, tts)
        print("再生完了")
    except Exception as exc:
        print(f"VOICEVOX再生テストに失敗: {exc}")
        print("VOICEVOX Engineの起動状態と chat_config.yaml の tts.voicevox.base_url を確認してください。")
        sys.exit(1)


if __name__ == "__main__":
    main()
