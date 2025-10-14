"""Cribbage card game engine.

This module implements the classic two-player Cribbage card game, featuring:
- The Deal: Each player gets 6 cards, discards 2 to the crib
- The Play (Pegging): Players alternate playing cards, scoring for pairs, runs, and 15s
- The Show: Both hands and the crib are scored for combinations
- First to 121 points wins

Rules:
* Standard 52-card deck
* Cards score: Ace=1, 2-10=face value, J/Q/K=10
* During play, score for reaching 15 (2 points), pairs (2 points), runs (length points)
* Cannot exceed 31 during play
* The Show scores: 15s (2 each), pairs (2 each), runs (length), flush (4-5), nobs (1)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from random import Random
from typing import Optional

from card_games.common.cards import RANK_TO_VALUE, Card, Deck


class GamePhase(Enum):
    """Current phase of the Cribbage game."""

    DEAL = auto()
    DISCARD = auto()
    PLAY = auto()
    SHOW = auto()
    GAME_OVER = auto()


@dataclass
class CribbageGame:
    """Cribbage game engine.

    Attributes:
        player1_hand: Player 1's hand
        player2_hand: Player 2's hand
        crib: The crib (dealer's extra hand)
        starter: The starter card (cut card)
        player1_score: Player 1's score
        player2_score: Player 2's score
        dealer: Current dealer (1 or 2)
        phase: Current game phase
        play_sequence: Cards played during pegging phase
        play_count: Running count during pegging
        winner: Winner of the game (1 or 2), None if ongoing
    """

    player1_hand: list[Card] = field(default_factory=list)
    player2_hand: list[Card] = field(default_factory=list)
    crib: list[Card] = field(default_factory=list)
    starter: Optional[Card] = None
    player1_score: int = 0
    player2_score: int = 0
    dealer: int = 1
    phase: GamePhase = GamePhase.DEAL
    play_sequence: list[tuple[int, Card]] = field(default_factory=list)
    play_count: int = 0
    current_player: int = 1
    winner: Optional[int] = None
    deck: Deck = field(default_factory=Deck)

    def __init__(self, rng: Optional[Random] = None) -> None:
        """Initialize a new Cribbage game.

        Args:
            rng: Optional Random instance for deterministic games
        """
        self.player1_hand = []
        self.player2_hand = []
        self.crib = []
        self.starter = None
        self.player1_score = 0
        self.player2_score = 0
        self.dealer = 1
        self.phase = GamePhase.DEAL
        self.play_sequence = []
        self.play_count = 0
        self.current_player = 1
        self.winner = None
        self.deck = Deck()
        self.deck.shuffle(rng=rng)
        self._deal_hands()

    def _deal_hands(self) -> None:
        """Deal 6 cards to each player."""
        self.player1_hand = [self.deck.cards.pop() for _ in range(6)]
        self.player2_hand = [self.deck.cards.pop() for _ in range(6)]
        self.phase = GamePhase.DISCARD

    def _card_value(self, card: Card) -> int:
        """Get the point value of a card for counting.

        Args:
            card: The card to evaluate

        Returns:
            Point value (1-10)
        """
        if card.rank in ["J", "Q", "K"]:
            return 10
        if card.rank == "A":
            return 1
        if card.rank == "T":
            return 10
        return int(card.rank)

    def discard_to_crib(self, player: int, cards: list[Card]) -> bool:
        """Discard 2 cards to the crib.

        Args:
            player: Player number (1 or 2)
            cards: Two cards to discard

        Returns:
            True if successful, False otherwise
        """
        if self.phase != GamePhase.DISCARD:
            return False

        if len(cards) != 2:
            return False

        hand = self.player1_hand if player == 1 else self.player2_hand

        if not all(card in hand for card in cards):
            return False

        # Remove from hand and add to crib
        for card in cards:
            hand.remove(card)
            self.crib.append(card)

        # Check if both players have discarded
        if len(self.crib) == 4:
            self._start_play()

        return True

    def _start_play(self) -> None:
        """Start the play (pegging) phase."""
        # Cut for starter
        if len(self.deck.cards) > 0:
            self.starter = self.deck.cards.pop()
        self.phase = GamePhase.PLAY
        # Non-dealer plays first
        self.current_player = 2 if self.dealer == 1 else 1

    def can_play_card(self, player: int, card: Card) -> bool:
        """Check if a card can be played.

        Args:
            player: Player number
            card: Card to play

        Returns:
            True if card can be played
        """
        if self.phase != GamePhase.PLAY:
            return False

        if player != self.current_player:
            return False

        hand = self.player1_hand if player == 1 else self.player2_hand
        if card not in hand:
            return False

        # Check if playing this card would exceed 31
        new_count = self.play_count + self._card_value(card)
        return new_count <= 31

    def play_card(self, player: int, card: Card) -> dict[str, any]:
        """Play a card during the pegging phase.

        Args:
            player: Player number
            card: Card to play

        Returns:
            Dictionary with play results and points scored
        """
        if not self.can_play_card(player, card):
            return {"success": False, "points": 0}

        hand = self.player1_hand if player == 1 else self.player2_hand
        hand.remove(card)

        self.play_sequence.append((player, card))
        self.play_count += self._card_value(card)

        points = self._score_play()

        # Add points to player's score
        if player == 1:
            self.player1_score += points
        else:
            self.player2_score += points

        # Check for win
        if self.player1_score >= 121:
            self.winner = 1
            self.phase = GamePhase.GAME_OVER
        elif self.player2_score >= 121:
            self.winner = 2
            self.phase = GamePhase.GAME_OVER

        # Switch players
        self.current_player = 2 if player == 1 else 1

        # Check if play should end
        if not self.player1_hand and not self.player2_hand:
            self.phase = GamePhase.SHOW

        return {
            "success": True,
            "points": points,
            "count": self.play_count,
            "game_over": self.phase == GamePhase.GAME_OVER,
        }

    def _score_play(self) -> int:
        """Score the current play sequence.

        Returns:
            Points scored
        """
        points = 0

        # Score for reaching 15
        if self.play_count == 15:
            points += 2

        # Score for reaching 31
        if self.play_count == 31:
            points += 2

        # Score for pairs
        if len(self.play_sequence) >= 2:
            last_card = self.play_sequence[-1][1]
            # Check for pair (2 points)
            if self.play_sequence[-2][1].rank == last_card.rank:
                points += 2
                # Check for three of a kind (6 points total)
                if len(self.play_sequence) >= 3 and self.play_sequence[-3][1].rank == last_card.rank:
                    points += 4
                    # Check for four of a kind (12 points total)
                    if len(self.play_sequence) >= 4 and self.play_sequence[-4][1].rank == last_card.rank:
                        points += 6

        # Score for runs (3+ cards in sequence)
        run_length = self._check_run()
        if run_length >= 3:
            points += run_length

        return points

    def _check_run(self) -> int:
        """Check for runs in the play sequence.

        Returns:
            Length of the run, or 0 if no run
        """
        if len(self.play_sequence) < 3:
            return 0

        # Check runs of different lengths
        for length in range(len(self.play_sequence), 2, -1):
            cards = [self.play_sequence[-i][1] for i in range(length, 0, -1)]
            values = sorted([RANK_TO_VALUE[c.rank] for c in cards])
            is_run = all(values[i] + 1 == values[i + 1] for i in range(len(values) - 1))
            if is_run:
                return length

        return 0

    def score_hand(self, hand: list[Card], is_crib: bool = False) -> int:
        """Score a hand for The Show.

        Args:
            hand: The hand to score
            is_crib: Whether this is the crib (affects flush scoring)

        Returns:
            Total points
        """
        if not self.starter:
            return 0

        points = 0
        all_cards = hand + [self.starter]

        # Score 15s (2 points each)
        points += self._score_fifteens(all_cards)

        # Score pairs (2 points each)
        points += self._score_pairs(all_cards)

        # Score runs
        points += self._score_runs(all_cards)

        # Score flush (4 or 5 points)
        flush_points = self._score_flush(hand, is_crib)
        points += flush_points

        # Score nobs (jack of same suit as starter, 1 point)
        points += self._score_nobs(hand)

        return points

    def _score_fifteens(self, cards: list[Card]) -> int:
        """Score all combinations that sum to 15.

        Args:
            cards: Cards to check

        Returns:
            Points scored (2 per fifteen)
        """
        count = 0
        n = len(cards)

        # Check all subsets
        for i in range(1, 2**n):
            subset_sum = sum(self._card_value(cards[j]) for j in range(n) if (i >> j) & 1)
            if subset_sum == 15:
                count += 1

        return count * 2

    def _score_pairs(self, cards: list[Card]) -> int:
        """Score pairs in the hand.

        Args:
            cards: Cards to check

        Returns:
            Points scored (2 per pair)
        """
        points = 0
        for i in range(len(cards)):
            for j in range(i + 1, len(cards)):
                if cards[i].rank == cards[j].rank:
                    points += 2
        return points

    def _score_runs(self, cards: list[Card]) -> int:
        """Score runs in the hand.

        Args:
            cards: Cards to check

        Returns:
            Points scored
        """
        # Check for runs of length 5, 4, then 3
        for run_length in [5, 4, 3]:
            if len(cards) < run_length:
                continue

            # Check all combinations of run_length cards
            from itertools import combinations

            for combo in combinations(cards, run_length):
                values = sorted([RANK_TO_VALUE[c.rank] for c in combo])
                is_run = all(values[i] + 1 == values[i + 1] for i in range(len(values) - 1))
                if is_run:
                    # Count how many such runs exist
                    count = sum(
                        1
                        for c in combinations(cards, run_length)
                        if all(
                            sorted([RANK_TO_VALUE[card.rank] for card in c])[i] + 1 == sorted([RANK_TO_VALUE[card.rank] for card in c])[i + 1]
                            for i in range(run_length - 1)
                        )
                    )
                    return run_length * count

        return 0

    def _score_flush(self, hand: list[Card], is_crib: bool) -> int:
        """Score flush in the hand.

        Args:
            hand: The hand to check
            is_crib: Whether this is the crib

        Returns:
            Points scored (4 or 5)
        """
        if len(hand) < 4:
            return 0

        # Check if all cards in hand are same suit
        first_suit = hand[0].suit
        if all(card.suit == first_suit for card in hand):
            # For crib, all 5 cards (including starter) must be same suit
            if is_crib:
                if self.starter and self.starter.suit == first_suit:
                    return 5
                return 0
            else:
                # For regular hand, 4 same suit = 4 points, 5 = 5 points
                if self.starter and self.starter.suit == first_suit:
                    return 5
                return 4

        return 0

    def _score_nobs(self, hand: list[Card]) -> int:
        """Score nobs (jack of same suit as starter).

        Args:
            hand: The hand to check

        Returns:
            Points scored (0 or 1)
        """
        if not self.starter:
            return 0

        for card in hand:
            if card.rank == "J" and card.suit == self.starter.suit:
                return 1

        return 0

    def get_state_summary(self) -> dict[str, any]:
        """Get a summary of the current game state.

        Returns:
            Dictionary with game state information
        """
        return {
            "player1_score": self.player1_score,
            "player2_score": self.player2_score,
            "dealer": self.dealer,
            "phase": self.phase.name,
            "play_count": self.play_count,
            "current_player": self.current_player,
            "player1_cards": len(self.player1_hand),
            "player2_cards": len(self.player2_hand),
            "crib_size": len(self.crib),
            "starter": str(self.starter) if self.starter else None,
            "winner": self.winner,
            "game_over": self.phase == GamePhase.GAME_OVER,
        }
