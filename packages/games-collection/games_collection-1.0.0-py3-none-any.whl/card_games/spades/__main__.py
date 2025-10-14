"""Entry point for the Spades game package."""

from __future__ import annotations

import argparse
import sys
from typing import Sequence

try:
    from tkinter import TclError
except Exception:  # pragma: no cover - Tkinter may be unavailable in some environments.
    _GUI_ERRORS: tuple[type[BaseException], ...] = (RuntimeError,)
else:
    _GUI_ERRORS = (RuntimeError, TclError)

from card_games.spades.cli import game_loop
from card_games.spades.gui import run_app


def main(argv: Sequence[str] | None = None) -> None:
    """Launch the GUI by default, falling back to the CLI when requested."""

    parser = argparse.ArgumentParser(description="Play Spades against AI opponents.")
    parser.add_argument("--cli", action="store_true", help="Run the text-based interface instead of the GUI.")
    parser.add_argument("--name", default="You", help="Display name for the GUI human player.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.cli:
        game_loop()
        return

    try:
        run_app(player_name=args.name)
    except _GUI_ERRORS as exc:
        print(f"{exc}\nFalling back to the command-line interface...", file=sys.stderr)
        game_loop()


if __name__ == "__main__":
    main()
