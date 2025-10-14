"""Sprouts game - topological graph game.

This is a basic implementation. Full version would include:
- Dot placement and connection mechanics
- Topological constraints
- AI opponent
"""

from __future__ import annotations

from typing import List, Optional, Set

from common.game_engine import GameEngine, GameState


class SproutsGame(GameEngine[tuple, int]):
    def __init__(self, initial_dots: int = 3) -> None:
        self._dots: Set[int] = set(range(initial_dots))
        self._connections = []
        self._current_player = 1
        self._state = GameState.IN_PROGRESS
        self._next_dot_id = initial_dots

    def reset(self) -> None:
        initial_dots = 3
        self._dots = set(range(initial_dots))
        self._connections = []
        self._current_player = 1
        self._state = GameState.IN_PROGRESS
        self._next_dot_id = initial_dots

    def is_game_over(self) -> bool:
        return self._state == GameState.FINISHED or len(self._dots) == 0

    def get_current_player(self) -> int:
        return self._current_player

    def get_valid_moves(self) -> List[tuple]:
        return [(a, b) for a in self._dots for b in self._dots]

    def make_move(self, move: tuple) -> bool:
        dot1, dot2 = move
        if dot1 not in self._dots or dot2 not in self._dots:
            return False
        self._connections.append((dot1, dot2, self._next_dot_id))
        self._dots.add(self._next_dot_id)
        self._next_dot_id += 1
        self._current_player = 3 - self._current_player
        return True

    def get_winner(self) -> Optional[int]:
        return 3 - self._current_player if self.is_game_over() else None

    def get_game_state(self) -> GameState:
        return self._state

    def get_state_representation(self) -> dict:
        return {"dots": list(self._dots), "connections": self._connections}


class SproutsCLI:
    def __init__(self) -> None:
        self.game = SproutsGame()

    def run(self) -> None:
        print("Sprouts - Basic Implementation")
        print("Full implementation coming soon!")
        print("This is a simplified topological game.")
