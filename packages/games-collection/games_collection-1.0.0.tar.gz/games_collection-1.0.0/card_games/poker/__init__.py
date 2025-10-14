"""Poker implementation within the Card Games collection."""

# Expose the primary gameplay types so callers can simply import from the
# package root instead of drilling into submodules.
from .poker import DIFFICULTIES, Action, ActionType, BotSkill, MatchResult, Player, PokerMatch, PokerTable, estimate_win_rate, run_cli

try:  # pragma: no cover - optional GUI dependency
    from .gui import PokerGUI, launch_gui
except Exception:  # pragma: no cover - gracefully degrade without Tk
    PokerGUI = None  # type: ignore[assignment]

    def launch_gui(*args, **kwargs):  # type: ignore[override]
        raise RuntimeError("Tkinter is required for the poker GUI but is not available.")


from .poker_core import HandCategory, HandRank, best_hand

__all__ = [
    "Action",
    "ActionType",
    "BotSkill",
    "DIFFICULTIES",
    "HandCategory",
    "HandRank",
    "MatchResult",
    "Player",
    "PokerMatch",
    "PokerTable",
    "PokerGUI",
    "best_hand",
    "estimate_win_rate",
    "launch_gui",
    "run_cli",
]
