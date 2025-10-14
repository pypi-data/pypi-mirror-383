"""Backgammon game - dice-based race game.

This is a basic implementation. Full version would include:
- Traditional backgammon board layout
- Bearing off mechanics
- Doubling cube
- AI opponent
"""

from __future__ import annotations

import random
from typing import List, Optional

from common.game_engine import GameEngine, GameState


class BackgammonGame(GameEngine[tuple, int]):
    def __init__(self) -> None:
        self._positions = [0] * 24  # Simplified board
        self._dice = [1, 1]
        self._current_player = 1
        self._state = GameState.IN_PROGRESS

    def reset(self) -> None:
        self._positions = [0] * 24
        self._current_player = 1
        self._state = GameState.IN_PROGRESS

    def is_game_over(self) -> bool:
        return self._state == GameState.FINISHED

    def get_current_player(self) -> int:
        return self._current_player

    def get_valid_moves(self) -> List[tuple]:
        return [(0, 1), (1, 2)]  # Simplified

    def make_move(self, move: tuple) -> bool:
        self._current_player = 3 - self._current_player
        return True

    def roll_dice(self) -> tuple:
        self._dice = [random.randint(1, 6), random.randint(1, 6)]
        return tuple(self._dice)

    def get_winner(self) -> Optional[int]:
        return None

    def get_game_state(self) -> GameState:
        return self._state

    def get_state_representation(self) -> dict:
        return {"positions": self._positions, "dice": self._dice}


class BackgammonCLI:
    def __init__(self) -> None:
        self.game = BackgammonGame()

    def run(self) -> None:
        print("Backgammon - Basic Implementation")
        print("Full implementation coming soon!")
        print("This is a simplified version.")
