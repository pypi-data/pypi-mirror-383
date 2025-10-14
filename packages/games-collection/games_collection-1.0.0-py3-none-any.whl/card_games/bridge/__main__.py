"""Command-line entry point for the Bridge package."""

from __future__ import annotations

import argparse
from typing import Optional

from card_games.bridge.cli import game_loop
from card_games.bridge.gui import run_app


def main(args: Optional[list[str]] = None) -> None:
    """Launch the Bridge game in CLI or GUI mode."""

    parser = argparse.ArgumentParser(description="Play a deal of Contract Bridge.")
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--cli", action="store_true", help="Launch the text-based interface.")
    mode_group.add_argument("--gui", action="store_true", help="Launch the graphical interface.")
    parsed = parser.parse_args(args)

    if parsed.cli:
        game_loop()
        return

    run_app()


if __name__ == "__main__":
    main()
