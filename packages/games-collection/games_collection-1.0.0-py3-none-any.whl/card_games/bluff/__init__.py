"""Bluff (Cheat) card game engine and user interfaces.

This module acts as the public API surface for the Bluff package. Importing it
exposes the key classes and helpers required to embed the engine in other
applications and highlights the available user interfaces (CLI and GUI) without
needing to dig into the implementation modules.
"""

# Provide a single import surface for the engine and helper utilities.
from .bluff import BluffGame, DifficultyLevel, Phase, run_cli

try:  # pragma: no cover - optional GUI dependency
    from .gui import BluffGUI, run_gui
except Exception:  # pragma: no cover - gracefully degrade without Tk
    BluffGUI = None  # type: ignore[assignment]

    def run_gui(*args, **kwargs):  # type: ignore[override]
        raise RuntimeError("Tkinter is required for the bluff GUI but is not available.")


__all__ = [
    "BluffGame",
    "DifficultyLevel",
    "Phase",
    "run_cli",
    "BluffGUI",
    "run_gui",
]
