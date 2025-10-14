"""Gin Rummy card game package."""

from .game import GinRummyGame, GinRummyPlayer

# GUI is optional (requires tkinter)
try:
    from .gui import GinRummyGUI, run_app

    __all__ = ["GinRummyGame", "GinRummyPlayer", "GinRummyGUI", "run_app"]
except ImportError:
    __all__ = ["GinRummyGame", "GinRummyPlayer"]
