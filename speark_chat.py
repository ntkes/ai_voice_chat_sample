from __future__ import annotations

from pathlib import Path
import argparse

from voice_chat_lib.chat_session import run_voice_chat


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Console voice chat")
	parser.add_argument(
		"--config",
		type=Path,
		default=Path("chat_config.yaml"),
		help="Path to config file (.yaml/.yml)",
	)
	return parser.parse_args()


def main() -> None:
	args = parse_args()
	# Delegate full chat lifecycle to the library module.
	run_voice_chat(args.config)


if __name__ == "__main__":
	main()
