"""Blackjack game package."""

# Re-export core types so ``card_games.blackjack`` behaves like a facade for
# both the engine and the GUI helper functions.
from .game import BlackjackGame, BlackjackHand, Outcome

# Make GUI imports optional (tkinter may not be available)
try:
    from .gui import BlackjackApp, run_app

    __all__ = ["BlackjackGame", "BlackjackHand", "Outcome", "BlackjackApp", "run_app"]
except ImportError:
    __all__ = ["BlackjackGame", "BlackjackHand", "Outcome"]
