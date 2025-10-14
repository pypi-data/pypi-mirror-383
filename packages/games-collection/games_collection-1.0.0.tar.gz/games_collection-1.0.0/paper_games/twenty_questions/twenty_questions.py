"""Core logic and CLI for 20 Questions.

AI-based guessing game using binary search tree strategy to narrow down
possibilities through yes/no questions.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Optional

from common.game_engine import GameEngine, GameState


@dataclass
class QuestionNode:
    """Node in the question decision tree."""

    question: str
    yes_branch: Optional[QuestionNode] = None
    no_branch: Optional[QuestionNode] = None
    answer: Optional[str] = None  # Leaf node with final answer


class TwentyQuestionsGame(GameEngine[str, int]):
    """20 Questions AI guessing game."""

    # Simple decision tree for common objects
    OBJECTS = {
        "animal": ["dog", "cat", "elephant", "bird", "fish", "lion", "tiger", "bear"],
        "food": ["pizza", "apple", "banana", "hamburger", "cake", "ice cream"],
        "vehicle": ["car", "bicycle", "airplane", "boat", "train", "helicopter"],
        "sport": ["soccer", "basketball", "tennis", "swimming", "baseball"],
    }

    def __init__(self) -> None:
        """Initialize 20 Questions game."""
        self._secret_object: Optional[str] = None
        self._questions_asked = 0
        self._max_questions = 20
        self._state = GameState.NOT_STARTED
        self._guessed_correct = False
        self._knowledge: Dict[str, bool] = {}  # Store yes/no answers
        self.reset()

    def reset(self) -> None:
        """Reset the game to initial state."""
        # Flatten all objects
        all_objects = []
        for objects in self.OBJECTS.values():
            all_objects.extend(objects)

        self._secret_object = random.choice(all_objects)
        self._questions_asked = 0
        self._state = GameState.IN_PROGRESS
        self._guessed_correct = False
        self._knowledge = {}

    def is_game_over(self) -> bool:
        """Check if the game has ended."""
        return self._state == GameState.FINISHED

    def get_current_player(self) -> int:
        """Get the current player (always 0 - AI)."""
        return 0

    def get_valid_moves(self) -> List[str]:
        """Get valid moves (possible questions or guesses)."""
        if self.is_game_over():
            return []
        return ["ask_question", "make_guess"]

    def make_move(self, move: str) -> bool:
        """Execute a move (ask question or make guess).

        Args:
            move: The move type ("ask_question" or "make_guess")

        Returns:
            True if move was valid
        """
        if self.is_game_over():
            return False
        # This is handled by ask_question() and make_guess()
        return True

    def ask_question(self, question: str, answer: bool) -> None:
        """Record a question and its answer.

        Args:
            question: The question asked
            answer: True for yes, False for no
        """
        if self.is_game_over():
            return

        self._questions_asked += 1
        self._knowledge[question] = answer

        if self._questions_asked >= self._max_questions:
            self._state = GameState.FINISHED

    def make_guess(self, guess: str) -> bool:
        """Make a guess at the secret object.

        Args:
            guess: The guessed object

        Returns:
            True if guess is correct
        """
        if self.is_game_over():
            return False

        self._questions_asked += 1

        if guess.lower() == self._secret_object.lower():
            self._guessed_correct = True
            self._state = GameState.FINISHED
            return True

        if self._questions_asked >= self._max_questions:
            self._state = GameState.FINISHED

        return False

    def get_winner(self) -> Optional[int]:
        """Get the winner if game is over."""
        if not self.is_game_over():
            return None
        return 0 if self._guessed_correct else None

    def get_game_state(self) -> GameState:
        """Get the current game state."""
        return self._state

    def get_state_representation(self) -> Dict[str, any]:
        """Get a representation of the game state."""
        return {
            "questions_asked": self._questions_asked,
            "questions_remaining": self._max_questions - self._questions_asked,
            "guessed_correct": self._guessed_correct,
        }

    def get_questions_remaining(self) -> int:
        """Get number of questions remaining."""
        return max(0, self._max_questions - self._questions_asked)

    def get_secret_object(self) -> Optional[str]:
        """Get the secret object (for debugging or after game ends)."""
        return self._secret_object


class TwentyQuestionsCLI:
    """Command line interface for 20 Questions."""

    def __init__(self) -> None:
        """Initialize the CLI."""
        self.game: Optional[TwentyQuestionsGame] = None

    def run(self) -> None:
        """Run the game loop."""
        print("Welcome to 20 Questions!")
        print("=" * 60)
        print("Think of an object, and I'll try to guess it!")
        print("Answer my questions with 'yes' or 'no'.")
        print()

        self.game = TwentyQuestionsGame()

        print("Categories: animal, food, vehicle, sport")
        print("Think of something from one of these categories...")
        input("Press Enter when you're ready...")
        print()

        # Simple question strategy
        questions = [
            "Is it a living thing?",
            "Is it an animal?",
            "Is it food?",
            "Is it a vehicle?",
            "Is it bigger than a person?",
            "Can you eat it?",
            "Does it have wheels?",
            "Does it fly?",
            "Is it a pet?",
            "Does it swim?",
        ]

        asked_questions = set()

        while not self.game.is_game_over():
            remaining = self.game.get_questions_remaining()
            print(f"Questions remaining: {remaining}")

            # Try to ask a question
            if remaining > 1:
                # Find an unasked question
                question = None
                for q in questions:
                    if q not in asked_questions:
                        question = q
                        break

                if question:
                    while True:
                        answer_str = input(f"\n{question} (yes/no): ").lower()
                        if answer_str in ["yes", "y", "no", "n"]:
                            break
                        print("Please answer with 'yes' or 'no'")

                    answer = answer_str in ["yes", "y"]
                    self.game.ask_question(question, answer)
                    asked_questions.add(question)
                else:
                    # Out of questions, make a guess
                    break
            else:
                # Last question - make a guess
                break

            # Try to narrow down based on answers
            if remaining <= 5:
                # Time to start guessing specific objects
                print("\nLet me think...")
                break

        # Make final guesses
        print("\nI think I know what it is!")

        # Get possible objects based on knowledge
        possible_objects = []
        for category, objects in self.game.OBJECTS.items():
            possible_objects.extend(objects)

        random.shuffle(possible_objects)

        for obj in possible_objects[:3]:  # Try up to 3 guesses
            if self.game.is_game_over():
                break

            guess = input(f"\nIs it a {obj}? (yes/no): ").lower()
            if guess in ["yes", "y"]:
                print("\n🎉 I guessed it! Thanks for playing! 🎉")
                return
            else:
                self.game._questions_asked += 1

        # Failed to guess
        print("\nI give up! What was it?")
        answer = input("What were you thinking of? ")
        print("\nInteresting! I'll remember that for next time.")
        print("Thanks for playing!")
