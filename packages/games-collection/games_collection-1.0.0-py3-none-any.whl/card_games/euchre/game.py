"""Euchre card game engine.

This module implements the classic four-player Euchre game with trump-based
trick-taking gameplay and the unique "going alone" mechanic.

Rules:
* 24-card deck (9, T, J, Q, K, A of each suit)
* Four players in two partnerships (1&3 vs 2&4)
* Trump suit selected after dealing
* Right bower (Jack of trump) is highest trump
* Left bower (Jack of same-color suit) is second highest trump
* First team to 10 points wins
* "Going alone" option for maker's partner to sit out
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from random import Random
from typing import Optional

from card_games.common.cards import Card, Suit


class GamePhase(Enum):
    """Current phase of the Euchre game."""

    DEAL = auto()
    BIDDING = auto()
    PLAY = auto()
    SCORE = auto()
    GAME_OVER = auto()


@dataclass
class EuchreGame:
    """Euchre game engine.

    Attributes:
        hands: Four player hands
        trump: Trump suit
        maker: Team that chose trump (1 or 2)
        dealer: Current dealer (0-3)
        current_trick: Cards in current trick
        tricks_won: Tricks won by each team
        team1_score: Team 1 score
        team2_score: Team 2 score
        phase: Current game phase
        going_alone: Whether someone is going alone
        winner: Winning team (1 or 2), None if ongoing
    """

    hands: list[list[Card]] = field(default_factory=lambda: [[], [], [], []])
    trump: Optional[Suit] = None
    maker: Optional[int] = None
    dealer: int = 0
    current_trick: list[tuple[int, Card]] = field(default_factory=list)
    tricks_won: list[int] = field(default_factory=lambda: [0, 0])
    team1_score: int = 0
    team2_score: int = 0
    phase: GamePhase = GamePhase.DEAL
    going_alone: bool = False
    alone_player: Optional[int] = None
    current_player: int = 0
    winner: Optional[int] = None

    def __init__(self, rng: Optional[Random] = None) -> None:
        """Initialize a new Euchre game.

        Args:
            rng: Optional Random instance for deterministic games
        """
        self.hands = [[], [], [], []]
        self.trump = None
        self.maker = None
        self.dealer = 0
        self.current_trick = []
        self.tricks_won = [0, 0]
        self.team1_score = 0
        self.team2_score = 0
        self.phase = GamePhase.DEAL
        self.going_alone = False
        self.alone_player = None
        self.current_player = 0
        self.winner = None
        self._rng = rng or Random()
        self._deal_hands()

    def _create_euchre_deck(self) -> list[Card]:
        """Create a 24-card Euchre deck (9-A in each suit).

        Returns:
            List of cards
        """
        ranks = ["9", "T", "J", "Q", "K", "A"]
        suits = [Suit.CLUBS, Suit.DIAMONDS, Suit.HEARTS, Suit.SPADES]
        return [Card(rank, suit) for suit in suits for rank in ranks]

    def _deal_hands(self) -> None:
        """Deal 5 cards to each player."""
        deck = self._create_euchre_deck()
        self._rng.shuffle(deck)

        for i in range(4):
            self.hands[i] = deck[i * 5 : (i + 1) * 5]

        self.phase = GamePhase.BIDDING
        self.current_player = (self.dealer + 1) % 4

    def select_trump(self, suit: Suit, player: int, go_alone: bool = False) -> bool:
        """Select trump suit.

        Args:
            suit: Trump suit to select
            player: Player selecting trump
            go_alone: Whether to go alone

        Returns:
            True if successful
        """
        if self.phase != GamePhase.BIDDING:
            return False

        self.trump = suit
        # Determine maker team (players 0&2 are team 1, players 1&3 are team 2)
        self.maker = 1 if player in [0, 2] else 2
        self.going_alone = go_alone
        self.alone_player = player if go_alone else None
        self.phase = GamePhase.PLAY
        self.current_player = (self.dealer + 1) % 4
        return True

    def _get_card_power(self, card: Card) -> int:
        """Get the power ranking of a card.

        Args:
            card: Card to evaluate

        Returns:
            Power ranking (higher is better)
        """
        if not self.trump:
            rank_values = {"9": 0, "T": 1, "J": 2, "Q": 3, "K": 4, "A": 5}
            return rank_values.get(card.rank, 0)

        # Right bower (Jack of trump) is highest
        if card.rank == "J" and card.suit == self.trump:
            return 100

        # Left bower (Jack of same color) is second highest
        same_color_suit = self._get_same_color_suit(self.trump)
        if same_color_suit and card.rank == "J" and card.suit == same_color_suit:
            return 99

        # Trump cards
        if card.suit == self.trump:
            rank_values = {"9": 80, "T": 81, "Q": 82, "K": 83, "A": 84}
            return rank_values.get(card.rank, 80)

        # Non-trump cards
        rank_values = {"9": 0, "T": 1, "J": 2, "Q": 3, "K": 4, "A": 5}
        return rank_values.get(card.rank, 0)

    def _get_same_color_suit(self, suit: Suit) -> Optional[Suit]:
        """Get the same-color suit.

        Args:
            suit: Input suit

        Returns:
            Same-color suit
        """
        if suit == Suit.CLUBS:
            return Suit.SPADES
        elif suit == Suit.SPADES:
            return Suit.CLUBS
        elif suit == Suit.HEARTS:
            return Suit.DIAMONDS
        elif suit == Suit.DIAMONDS:
            return Suit.HEARTS
        return None

    def play_card(self, player: int, card: Card) -> dict[str, any]:
        """Play a card.

        Args:
            player: Player number (0-3)
            card: Card to play

        Returns:
            Result dictionary
        """
        if self.phase != GamePhase.PLAY:
            return {"success": False, "message": "Not in play phase"}

        if player != self.current_player:
            return {"success": False, "message": "Not your turn"}

        if card not in self.hands[player]:
            return {"success": False, "message": "Card not in hand"}

        # Play the card
        self.hands[player].remove(card)
        self.current_trick.append((player, card))

        # Check if trick is complete
        if len(self.current_trick) == 4 or (self.going_alone and len(self.current_trick) == 3):
            winner = self._determine_trick_winner()
            team = 1 if winner in [0, 2] else 2
            self.tricks_won[team - 1] += 1
            self.current_trick = []

            # Check if hand is complete
            if all(len(hand) == 0 for hand in self.hands):
                self._score_hand()
                if self.team1_score >= 10 or self.team2_score >= 10:
                    self.phase = GamePhase.GAME_OVER
                    self.winner = 1 if self.team1_score >= 10 else 2
                else:
                    # Deal new hand
                    self.dealer = (self.dealer + 1) % 4
                    self._deal_hands()
            else:
                self.current_player = winner
        else:
            self.current_player = (self.current_player + 1) % 4
            # Skip partner if going alone
            if self.going_alone and self.alone_player is not None:
                partner = (self.alone_player + 2) % 4
                if self.current_player == partner:
                    self.current_player = (self.current_player + 1) % 4

        return {"success": True, "trick_complete": len(self.current_trick) == 0}

    def _determine_trick_winner(self) -> int:
        """Determine the winner of the current trick.

        Returns:
            Player number who won
        """
        if not self.current_trick:
            return 0

        # Find highest card
        best_player = self.current_trick[0][0]
        best_power = self._get_card_power(self.current_trick[0][1])

        for player, card in self.current_trick[1:]:
            power = self._get_card_power(card)
            if power > best_power:
                best_player = player
                best_power = power

        return best_player

    def _score_hand(self) -> None:
        """Score the completed hand."""
        making_team = self.maker
        if making_team is None:
            return

        defending_team = 2 if making_team == 1 else 1
        making_tricks = self.tricks_won[making_team - 1]

        if making_tricks >= 3:
            # Makers won
            if making_tricks == 5:
                # March
                points = 4 if self.going_alone else 2
            else:
                # Made it
                points = 2 if self.going_alone else 1
            if making_team == 1:
                self.team1_score += points
            else:
                self.team2_score += points
        else:
            # Euchred - defenders get 2 points
            if defending_team == 1:
                self.team1_score += 2
            else:
                self.team2_score += 2

        self.tricks_won = [0, 0]

    def get_state_summary(self) -> dict[str, any]:
        """Get game state summary.

        Returns:
            State dictionary
        """
        return {
            "team1_score": self.team1_score,
            "team2_score": self.team2_score,
            "dealer": self.dealer,
            "phase": self.phase.name,
            "trump": str(self.trump) if self.trump else None,
            "maker": self.maker,
            "tricks_won": self.tricks_won,
            "current_player": self.current_player,
            "going_alone": self.going_alone,
            "winner": self.winner,
            "game_over": self.phase == GamePhase.GAME_OVER,
        }
