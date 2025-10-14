"""Hearts card game package."""

from .game import HeartsGame, HeartsPlayer

# GUI is optional (requires tkinter)
try:
    from .gui import HeartsGUI, run_app

    __all__ = ["HeartsGame", "HeartsPlayer", "HeartsGUI", "run_app"]
except (ImportError, RuntimeError):
    # tkinter not available or GUI module raised RuntimeError
    __all__ = ["HeartsGame", "HeartsPlayer"]
