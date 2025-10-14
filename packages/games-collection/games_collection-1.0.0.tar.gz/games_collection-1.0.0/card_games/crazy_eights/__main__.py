"""Entry point for Crazy Eights card game."""

from __future__ import annotations

import argparse
import random

from card_games.crazy_eights.cli import game_loop
from card_games.crazy_eights.game import CrazyEightsGame
from common.gui_base import TKINTER_AVAILABLE


def main() -> None:
    """Main entry point for the Crazy Eights game."""
    parser = argparse.ArgumentParser(description="Play the card game Crazy Eights")
    parser.add_argument("--players", type=int, default=2, choices=range(2, 7), help="Number of players (2-6)")
    parser.add_argument("--seed", type=int, help="Random seed for reproducible games")
    parser.add_argument("--names", nargs="+", help="Player names")
    parser.add_argument("--draw-limit", type=int, default=3, help="Max cards to draw when unable to play (0 = unlimited)")
    parser.add_argument("--cli", action="store_true", help="Run the command-line interface instead of the GUI")
    args = parser.parse_args()

    rng = None
    if args.seed is not None:
        rng = random.Random(args.seed)

    player_names = args.names if args.names else None
    game = CrazyEightsGame(num_players=args.players, player_names=player_names, draw_limit=args.draw_limit, rng=rng)

    if args.cli or not TKINTER_AVAILABLE:
        if not TKINTER_AVAILABLE and not args.cli:
            print("Tkinter is not available. Falling back to the CLI interface.")
        game_loop(game)
        return

    import tkinter as tk

    from card_games.crazy_eights.gui import CrazyEightsGUI

    try:
        root = tk.Tk()
    except tk.TclError as exc:
        print(f"Unable to start the Crazy Eights GUI: {exc}. Falling back to the CLI interface.")
        game_loop(game)
        return

    CrazyEightsGUI(root, game)
    root.mainloop()


if __name__ == "__main__":
    main()
