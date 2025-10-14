"""Rummy 500 card game engine.

This module implements Rummy 500, a variant of rummy with melding, laying off,
and negative scoring for cards remaining in hand.

Rules:
* Standard 52-card deck
* 2-4 players
* Goal: Be first to reach 500 points
* Score points for melds (sets and runs)
* Lose points for cards left in hand
* Can pick from discard pile and see all discarded cards
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from random import Random
from typing import Optional

from card_games.common.cards import RANK_TO_VALUE, Card, Deck


class GamePhase(Enum):
    """Current phase of Rummy 500."""

    DEAL = auto()
    DRAW = auto()
    MELD = auto()
    DISCARD = auto()
    GAME_OVER = auto()


@dataclass
class Rummy500Game:
    """Rummy 500 game engine.

    Attributes:
        hands: Player hands
        melds: Melds laid down by each player
        discard_pile: Discard pile (visible)
        deck: Draw deck
        scores: Player scores
        current_player: Current player
        phase: Current game phase
        winner: Winner (player index), None if ongoing
    """

    hands: list[list[Card]] = field(default_factory=list)
    melds: list[list[list[Card]]] = field(default_factory=list)
    discard_pile: list[Card] = field(default_factory=list)
    deck: Deck = field(default_factory=Deck)
    scores: list[int] = field(default_factory=list)
    current_player: int = 0
    phase: GamePhase = GamePhase.DEAL
    winner: Optional[int] = None
    num_players: int = 2

    def __init__(self, num_players: int = 2, rng: Optional[Random] = None) -> None:
        """Initialize Rummy 500 game.

        Args:
            num_players: Number of players (2-4)
            rng: Optional Random instance
        """
        self.num_players = max(2, min(4, num_players))
        self.hands = [[] for _ in range(self.num_players)]
        self.melds = [[] for _ in range(self.num_players)]
        self.discard_pile = []
        self.deck = Deck()
        self.scores = [0] * self.num_players
        self.current_player = 0
        self.phase = GamePhase.DEAL
        self.winner = None

        if rng:
            self.deck.shuffle(rng=rng)
        else:
            self.deck.shuffle()

        self._deal_hands()

    def _deal_hands(self) -> None:
        """Deal initial hands."""
        cards_per_player = 7 if self.num_players == 2 else 7
        for i in range(self.num_players):
            self.hands[i] = [self.deck.deal() for _ in range(cards_per_player)]

        # Start discard pile
        if len(self.deck.cards) > 0:
            self.discard_pile.append(self.deck.deal())

        self.phase = GamePhase.DRAW

    def _card_value(self, card: Card) -> int:
        """Get point value of a card.

        Args:
            card: Card to evaluate

        Returns:
            Point value
        """
        if card.rank == "A":
            return 15
        elif card.rank in ["J", "Q", "K"]:
            return 10
        elif card.rank == "T":
            return 10
        else:
            return int(card.rank)

    def draw_card(self, from_discard: bool = False, take_count: int = 1) -> bool:
        """Draw a card.

        Args:
            from_discard: Whether to draw from discard pile
            take_count: Number of cards to take from discard

        Returns:
            True if successful
        """
        if self.phase != GamePhase.DRAW:
            return False

        if from_discard:
            if len(self.discard_pile) >= take_count:
                # Take cards from discard pile
                for _ in range(take_count):
                    card = self.discard_pile.pop()
                    self.hands[self.current_player].append(card)
            else:
                return False
        else:
            # Draw from deck
            if len(self.deck.cards) > 0:
                card = self.deck.deal()
                self.hands[self.current_player].append(card)
            else:
                # Reshuffle discard pile if deck empty
                if len(self.discard_pile) > 1:
                    top_discard = self.discard_pile.pop()
                    self.deck.cards = self.discard_pile[:]
                    self.deck.shuffle()
                    self.discard_pile = [top_discard]
                    card = self.deck.deal()
                    self.hands[self.current_player].append(card)
                else:
                    return False

        self.phase = GamePhase.MELD
        return True

    def is_valid_meld(self, cards: list[Card]) -> bool:
        """Check if cards form a valid meld.

        Args:
            cards: Cards to check

        Returns:
            True if valid meld
        """
        if len(cards) < 3:
            return False

        # Check for set (same rank)
        if all(c.rank == cards[0].rank for c in cards):
            return True

        # Check for run (consecutive ranks, same suit)
        if all(c.suit == cards[0].suit for c in cards):
            values = sorted([RANK_TO_VALUE[c.rank] for c in cards])
            return all(values[i] + 1 == values[i + 1] for i in range(len(values) - 1))

        return False

    def lay_meld(self, player: int, cards: list[Card]) -> bool:
        """Lay down a meld.

        Args:
            player: Player laying meld
            cards: Cards in the meld

        Returns:
            True if successful
        """
        if not self.is_valid_meld(cards):
            return False

        if not all(c in self.hands[player] for c in cards):
            return False

        # Remove from hand and add to melds
        for card in cards:
            self.hands[player].remove(card)

        self.melds[player].append(cards)
        return True

    def discard(self, player: int, card: Card) -> bool:
        """Discard a card.

        Args:
            player: Player discarding
            card: Card to discard

        Returns:
            True if successful
        """
        if card not in self.hands[player]:
            return False

        self.hands[player].remove(card)
        self.discard_pile.append(card)

        # Check if hand is empty (going out)
        if not self.hands[player]:
            self._score_round()
            if any(s >= 500 for s in self.scores):
                self.phase = GamePhase.GAME_OVER
                self.winner = self.scores.index(max(self.scores))
            else:
                # Start new round
                self.__init__(self.num_players)
        else:
            # Next player
            self.current_player = (self.current_player + 1) % self.num_players
            self.phase = GamePhase.DRAW

        return True

    def _score_round(self) -> None:
        """Score the round when someone goes out."""
        for i in range(self.num_players):
            points = 0

            # Score melds
            for meld in self.melds[i]:
                points += sum(self._card_value(c) for c in meld)

            # Subtract cards in hand
            points -= sum(self._card_value(c) for c in self.hands[i])

            self.scores[i] += points

    def get_state_summary(self) -> dict[str, any]:
        """Get game state summary.

        Returns:
            State dictionary
        """
        return {
            "scores": self.scores,
            "current_player": self.current_player,
            "phase": self.phase.name,
            "hand_sizes": [len(h) for h in self.hands],
            "discard_top": str(self.discard_pile[-1]) if self.discard_pile else None,
            "deck_size": len(self.deck.cards),
            "winner": self.winner,
            "game_over": self.phase == GamePhase.GAME_OVER,
        }
