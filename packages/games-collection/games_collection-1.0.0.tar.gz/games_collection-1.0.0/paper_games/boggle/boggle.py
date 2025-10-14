"""Core logic and CLI for Boggle.

Word search game in a random letter grid with dictionary validation.
Players find words by connecting adjacent letters.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Optional, Set

from common.game_engine import GameEngine, GameState


@dataclass(frozen=True)
class BoggleMove:
    """Representation of a Boggle move (a found word)."""

    word: str


class BoggleGame(GameEngine[BoggleMove, int]):
    """Boggle word search game."""

    VOWELS = "AEIOU"
    CONSONANTS = "BCDFGHJKLMNPQRSTVWXYZ"

    # Basic English word list - in real implementation would use full dictionary
    DICTIONARY = {
        "the",
        "and",
        "for",
        "are",
        "but",
        "not",
        "you",
        "all",
        "can",
        "her",
        "was",
        "one",
        "our",
        "out",
        "day",
        "get",
        "has",
        "him",
        "his",
        "how",
        "man",
        "new",
        "now",
        "old",
        "see",
        "two",
        "way",
        "who",
        "boy",
        "did",
        "its",
        "let",
        "put",
        "say",
        "she",
        "too",
        "use",
        "cat",
        "dog",
        "hat",
        "rat",
        "bat",
        "mat",
        "sat",
        "fat",
        "pat",
        "run",
        "sun",
        "fun",
        "gun",
        "bun",
        "pun",
        "top",
        "pot",
        "hot",
        "got",
        "lot",
        "dot",
        "not",
        "cot",
    }

    def __init__(self, size: int = 4, time_limit: int = 180) -> None:
        """Initialize Boggle game.

        Args:
            size: Grid size (default 4x4)
            time_limit: Time limit in seconds
        """
        self.size = size
        self.time_limit = time_limit
        self._grid: List[List[str]] = []
        self._found_words: Set[str] = set()
        self._score = 0
        self._state = GameState.NOT_STARTED
        self.reset()

    def reset(self) -> None:
        """Reset the game to initial state."""
        # Generate random letter grid
        self._grid = []
        for _ in range(self.size):
            row = []
            for _ in range(self.size):
                # 40% chance of vowel for better word formation
                if random.random() < 0.4:
                    row.append(random.choice(self.VOWELS))
                else:
                    row.append(random.choice(self.CONSONANTS))
            self._grid.append(row)

        self._found_words = set()
        self._score = 0
        self._state = GameState.IN_PROGRESS

    def is_game_over(self) -> bool:
        """Check if the game has ended."""
        return self._state == GameState.FINISHED

    def get_current_player(self) -> int:
        """Get the current player (always 0 for single player)."""
        return 0

    def get_valid_moves(self) -> List[BoggleMove]:
        """Get valid moves (all possible words in dictionary)."""
        # Too many to list - return empty
        return []

    def is_word_in_grid(self, word: str) -> bool:
        """Check if a word can be formed in the grid.

        Args:
            word: The word to check

        Returns:
            True if word can be formed by adjacent letters
        """
        word = word.upper()

        # Try starting from each position
        for row in range(self.size):
            for col in range(self.size):
                if self._search_from(word, 0, row, col, set()):
                    return True
        return False

    def _search_from(self, word: str, pos: int, row: int, col: int, visited: Set) -> bool:
        """Recursively search for word from position.

        Args:
            word: Word to search for
            pos: Current position in word
            row: Current row
            col: Current column
            visited: Set of visited positions

        Returns:
            True if word can be formed from this position
        """
        if pos >= len(word):
            return True

        if row < 0 or row >= self.size or col < 0 or col >= self.size:
            return False

        if (row, col) in visited:
            return False

        if self._grid[row][col] != word[pos]:
            return False

        # Found matching letter
        visited = visited | {(row, col)}

        # Check all adjacent positions
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                if self._search_from(word, pos + 1, row + dr, col + dc, visited):
                    return True

        return False

    def make_move(self, move: BoggleMove) -> bool:
        """Execute a move (submit a word).

        Args:
            move: The word to submit

        Returns:
            True if word is valid and not already found
        """
        if self.is_game_over():
            return False

        word = move.word.lower()

        # Check if already found
        if word in self._found_words:
            return False

        # Check if in dictionary
        if word not in self.DICTIONARY:
            return False

        # Check if can be formed in grid
        if not self.is_word_in_grid(word):
            return False

        # Valid word!
        self._found_words.add(word)
        # Score based on word length
        self._score += len(word) if len(word) <= 4 else len(word) * 2
        return True

    def end_game(self) -> None:
        """End the game."""
        self._state = GameState.FINISHED

    def get_winner(self) -> Optional[int]:
        """Get the winner (always player if game ended)."""
        return 0 if self.is_game_over() else None

    def get_game_state(self) -> GameState:
        """Get the current game state."""
        return self._state

    def get_state_representation(self) -> dict:
        """Get a representation of the game state."""
        return {
            "grid": [row.copy() for row in self._grid],
            "found_words": list(self._found_words),
            "score": self._score,
        }

    def get_grid(self) -> List[List[str]]:
        """Get the letter grid."""
        return [row.copy() for row in self._grid]

    def get_score(self) -> int:
        """Get the current score."""
        return self._score

    def get_found_words(self) -> Set[str]:
        """Get the set of found words."""
        return self._found_words.copy()


class BoggleCLI:
    """Command line interface for Boggle."""

    def __init__(self) -> None:
        """Initialize the CLI."""
        self.game: Optional[BoggleGame] = None

    def run(self) -> None:
        """Run the game loop."""
        print("Welcome to Boggle!")
        print("=" * 60)
        print("Find words by connecting adjacent letters (including diagonals)")
        print("Longer words score more points!")
        print()

        self.game = BoggleGame()

        # Show grid
        print("Your Boggle Board:")
        print("-" * 25)
        for row in self.game.get_grid():
            print("  " + "  ".join(row))
        print("-" * 25)
        print()

        print("Enter words one at a time, or 'done' to finish.")
        print()

        # Game loop
        while not self.game.is_game_over():
            word = input("Enter word (or 'done' to end): ").strip().lower()

            if word == "done":
                self.game.end_game()
                break

            if len(word) < 3:
                print("Words must be at least 3 letters!")
                continue

            move = BoggleMove(word=word)
            if self.game.make_move(move):
                points = len(word) if len(word) <= 4 else len(word) * 2
                print(f"✓ '{word}' is valid! +{points} points")
            else:
                if word in self.game.get_found_words():
                    print(f"✗ You already found '{word}'")
                elif word in self.game.DICTIONARY:
                    print(f"✗ '{word}' is not in the grid")
                else:
                    print(f"✗ '{word}' is not in the dictionary")

            print(f"Score: {self.game.get_score()}")
            print()

        # Game over
        print(f"\n{'=' * 60}")
        print("Game Over!")
        print(f"Final Score: {self.game.get_score()}")
        print(f"Words Found: {len(self.game.get_found_words())}")
        print(f"Words: {', '.join(sorted(self.game.get_found_words()))}")
        print(f"{'=' * 60}")
