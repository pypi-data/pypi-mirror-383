"""Pentago game - rotating quadrant board game.

This is a basic implementation. Full version would include:
- 6x6 board with four 3x3 quadrants that can rotate
- Win condition: 5 in a row
- AI opponent with minimax
"""

from __future__ import annotations

from typing import List, Optional

from common.game_engine import GameEngine, GameState


class PentagoGame(GameEngine[tuple, int]):
    def __init__(self) -> None:
        self._board = [[0] * 6 for _ in range(6)]
        self._current_player = 1
        self._state = GameState.IN_PROGRESS

    def reset(self) -> None:
        self._board = [[0] * 6 for _ in range(6)]
        self._current_player = 1
        self._state = GameState.IN_PROGRESS

    def is_game_over(self) -> bool:
        return self._state == GameState.FINISHED

    def get_current_player(self) -> int:
        return self._current_player

    def get_valid_moves(self) -> List[tuple]:
        return [(r, c) for r in range(6) for c in range(6) if self._board[r][c] == 0]

    def make_move(self, move: tuple) -> bool:
        r, c = move
        if self._board[r][c] != 0:
            return False
        self._board[r][c] = self._current_player
        self._current_player = 3 - self._current_player
        return True

    def get_winner(self) -> Optional[int]:
        return None

    def get_game_state(self) -> GameState:
        return self._state

    def get_state_representation(self) -> dict:
        return {"board": self._board}


class PentagoCLI:
    def __init__(self) -> None:
        self.game = PentagoGame()

    def run(self) -> None:
        print("Pentago - Basic Implementation")
        print("Full implementation coming soon!")
        print("This version has a 6x6 board without rotation.")
