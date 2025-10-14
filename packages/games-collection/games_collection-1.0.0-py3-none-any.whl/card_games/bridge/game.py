"""Bridge game engine.

This module models a single deal of Contract Bridge including bidding logic,
card play, and rubber-style scoring. While still streamlined, the implementation
now mirrors more realistic bridge concepts such as vulnerability, doubles and
redoubles, declarer determination, and heuristic AI for both bidding and play.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, Optional

from card_games.common.cards import Card, Deck, Suit


class BidSuit(Enum):
    """Bid suits in Bridge ordered by ascending rank."""

    CLUBS = 1
    DIAMONDS = 2
    HEARTS = 3
    SPADES = 4
    NO_TRUMP = 5


@dataclass(frozen=True)
class Bid:
    """Representation of a contract bid."""

    level: int
    suit: BidSuit

    def score(self) -> int:
        """Return a monotonically increasing value for bid comparison."""

        return self.level * 10 + self.suit.value


@dataclass
class Contract:
    """Represents the final contract for the deal."""

    bid: Bid
    declarer: "BridgePlayer"
    doubled: bool = False
    redoubled: bool = False


@dataclass
class BridgePlayer:
    """Represents a bridge participant."""

    name: str
    hand: list[Card] = field(default_factory=list)
    tricks_won: int = 0
    is_ai: bool = False
    partner_index: Optional[int] = None
    position: str = ""


class CallType(Enum):
    """Possible bidding calls."""

    BID = "bid"
    PASS = "pass"
    DOUBLE = "double"
    REDOUBLE = "redouble"


@dataclass
class Call:
    """A single call made during the auction."""

    player: BridgePlayer
    call_type: CallType
    bid: Optional[Bid] = None


class Vulnerability(Enum):
    """Vulnerability state for a deal."""

    NONE = "None"
    NORTH_SOUTH = "North/South"
    EAST_WEST = "East/West"
    BOTH = "Both"


SUIT_ORDER = {
    Suit.SPADES: 0,
    Suit.HEARTS: 1,
    Suit.DIAMONDS: 2,
    Suit.CLUBS: 3,
}


class BridgeGame:
    """Main engine for Contract Bridge."""

    def __init__(
        self,
        players: list[BridgePlayer],
        *,
        vulnerability: Vulnerability = Vulnerability.NONE,
        rng=None,
    ) -> None:
        """Initialise a bridge game instance.

        Args:
            players: The four players, ordered clockwise starting from North.
            vulnerability: Deal vulnerability applied to partnerships.
            rng: Optional deterministic random generator for shuffling.

        Raises:
            ValueError: If ``players`` does not contain exactly four entries.
        """

        if len(players) != 4:
            raise ValueError("Bridge requires exactly 4 players")

        self.players = players
        positions = ["N", "S", "E", "W"]
        for index, player in enumerate(self.players):
            player.position = positions[index]
            player.partner_index = (index + 2) % 4

        self.vulnerability = vulnerability
        self.rng = rng
        self.deck = Deck()
        self.contract: Optional[Contract] = None
        self.current_trick: list[tuple[BridgePlayer, Card]] = []
        self.lead_suit: Optional[Suit] = None
        self.trump_suit: Optional[Suit] = None
        self.dealer_index = 0
        self.declarer_index: Optional[int] = None
        self.bidding_history: list[Call] = []

    # ------------------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------------------
    def partnership_for(self, player: BridgePlayer) -> str:
        """Return the partnership identifier ("NS" or "EW") for ``player``."""

        return "NS" if player.position in {"N", "S"} else "EW"

    def _hand_distribution(self, cards: Iterable[Card]) -> Counter[Suit]:
        """Return suit counts for ``cards``."""

        return Counter(card.suit for card in cards)

    def _is_balanced(self, distribution: Counter[Suit]) -> bool:
        """Determine whether a hand is balanced."""

        counts = sorted(distribution.get(suit, 0) for suit in Suit)
        return counts in ([2, 3, 4, 4], [2, 3, 3, 5], [3, 3, 3, 4])

    def _bid_suit_to_card_suit(self, bid_suit: BidSuit) -> Optional[Suit]:
        """Map a bidding suit to a physical suit."""

        mapping = {
            BidSuit.CLUBS: Suit.CLUBS,
            BidSuit.DIAMONDS: Suit.DIAMONDS,
            BidSuit.HEARTS: Suit.HEARTS,
            BidSuit.SPADES: Suit.SPADES,
        }
        return mapping.get(bid_suit)

    def _sort_hand(self, player: BridgePlayer) -> None:
        """Sort a player's hand in a conventional order."""

        player.hand.sort(key=lambda card: (SUIT_ORDER[card.suit], card.value), reverse=True)

    # ------------------------------------------------------------------
    # Dealing
    # ------------------------------------------------------------------
    def deal_cards(self) -> None:
        """Deal 13 cards to each player and reset round state.

        The deck is reshuffled before dealing. Player trick counts, bidding
        history, and contract information are cleared.
        """

        self.deck = Deck()
        if self.rng is not None:
            self.deck.shuffle(rng=self.rng)
        else:
            self.deck.shuffle()

        for player in self.players:
            player.hand = []
            player.tricks_won = 0

        for _ in range(13):
            for player in self.players:
                player.hand.append(self.deck.deal(1)[0])

        for player in self.players:
            self._sort_hand(player)

        self.contract = None
        self.declarer_index = None
        self.trump_suit = None
        self.lead_suit = None
        self.current_trick = []
        self.bidding_history = []

    # ------------------------------------------------------------------
    # Bidding utilities
    # ------------------------------------------------------------------
    def evaluate_hand(self, player: BridgePlayer) -> int:
        """Calculate the high card point total for a hand.

        Args:
            player: The player whose hand should be evaluated.

        Returns:
            The standard high card point value for the hand.
        """

        score = 0
        for card in player.hand:
            if card.rank == "A":
                score += 4
            elif card.rank == "K":
                score += 3
            elif card.rank == "Q":
                score += 2
            elif card.rank == "J":
                score += 1
        return score

    def _current_highest_bid(self, history: list[Call]) -> Optional[Bid]:
        """Return the current highest bid from ``history``."""

        for call in reversed(history):
            if call.call_type == CallType.BID and call.bid is not None:
                return call.bid
        return None

    def _last_non_pass_call(self, history: list[Call]) -> Optional[Call]:
        """Return the most recent non-pass call."""

        for call in reversed(history):
            if call.call_type != CallType.PASS:
                return call
        return None

    def _last_bid_from_partnership(self, history: list[Call], partnership: str) -> Optional[Call]:
        """Return the latest bid made by ``partnership``."""

        for call in reversed(history):
            if call.call_type == CallType.BID and self.partnership_for(call.player) == partnership:
                return call
        return None

    def _construct_bid(self, suit: BidSuit, desired_level: int, current_bid: Optional[Bid]) -> Optional[Bid]:
        """Return a legal bid at or above ``desired_level`` over ``current_bid``."""

        level = max(1, desired_level)
        while level <= 7:
            candidate = Bid(level, suit)
            if current_bid is None or candidate.score() > current_bid.score():
                return candidate
            level += 1
        return None

    def _suggest_opening_call(
        self,
        player: BridgePlayer,
        hcp: int,
        distribution: Counter[Suit],
        current_bid: Optional[Bid],
    ) -> Call:
        """Suggest an opening call for ``player``."""

        longest = distribution.most_common()
        longest_suit, length = longest[0]
        bid_suit_map = {
            Suit.CLUBS: BidSuit.CLUBS,
            Suit.DIAMONDS: BidSuit.DIAMONDS,
            Suit.HEARTS: BidSuit.HEARTS,
            Suit.SPADES: BidSuit.SPADES,
        }

        if 15 <= hcp <= 17 and self._is_balanced(distribution):
            bid = self._construct_bid(BidSuit.NO_TRUMP, 1, current_bid)
            if bid is not None:
                return Call(player, CallType.BID, bid)

        if 20 <= hcp <= 21 and self._is_balanced(distribution):
            bid = self._construct_bid(BidSuit.NO_TRUMP, 2, current_bid)
            if bid is not None:
                return Call(player, CallType.BID, bid)

        if hcp >= 22:
            bid = self._construct_bid(BidSuit.CLUBS, 2, current_bid)
            if bid is not None:
                return Call(player, CallType.BID, bid)

        if hcp <= 11 and length >= 6:
            preempt_level = 3 if length >= 7 else 2
            bid = self._construct_bid(bid_suit_map[longest_suit], preempt_level, current_bid)
            if bid is not None:
                return Call(player, CallType.BID, bid)

        if hcp >= 12 or (hcp >= 11 and length >= 5):
            preferred = max(longest, key=lambda item: (item[1], bid_suit_map[item[0]].value))
            bid = self._construct_bid(bid_suit_map[preferred[0]], 1, current_bid)
            if bid is not None:
                return Call(player, CallType.BID, bid)

        return Call(player, CallType.PASS)

    def _suggest_response_call(
        self,
        player: BridgePlayer,
        hcp: int,
        distribution: Counter[Suit],
        partner_call: Call,
        current_bid: Optional[Bid],
    ) -> Call:
        """Suggest a response to partner's bid."""

        assert partner_call.bid is not None
        bid_suit = partner_call.bid.suit
        suit = self._bid_suit_to_card_suit(bid_suit)
        support = distribution.get(suit, 0) if suit else 0

        if bid_suit == BidSuit.NO_TRUMP:
            if hcp >= 10:
                bid = self._construct_bid(BidSuit.NO_TRUMP, 3, current_bid)
                if bid is not None:
                    return Call(player, CallType.BID, bid)
            elif hcp >= 8:
                bid = self._construct_bid(BidSuit.NO_TRUMP, 2, current_bid)
                if bid is not None:
                    return Call(player, CallType.BID, bid)
            return Call(player, CallType.PASS)

        if support >= 4 and hcp >= 13:
            game_level = 4 if bid_suit in {BidSuit.HEARTS, BidSuit.SPADES} else 5
            bid = self._construct_bid(bid_suit, game_level, current_bid)
            if bid is not None:
                return Call(player, CallType.BID, bid)

        if support >= 3 and hcp >= 10:
            bid = self._construct_bid(bid_suit, partner_call.bid.level + 2, current_bid)
            if bid is not None:
                return Call(player, CallType.BID, bid)

        if support >= 3 and hcp >= 6:
            bid = self._construct_bid(bid_suit, partner_call.bid.level + 1, current_bid)
            if bid is not None:
                return Call(player, CallType.BID, bid)

        # Consider bidding a new suit with a strong five-card holding.
        strong_suits = [(suit_key, count) for suit_key, count in distribution.items() if count >= 5 and suit_key != suit]
        if hcp >= 10 and strong_suits:
            chosen = max(strong_suits, key=lambda item: (item[1], SUIT_ORDER[item[0]] * -1))
            mapping = {
                Suit.CLUBS: BidSuit.CLUBS,
                Suit.DIAMONDS: BidSuit.DIAMONDS,
                Suit.HEARTS: BidSuit.HEARTS,
                Suit.SPADES: BidSuit.SPADES,
            }
            bid = self._construct_bid(mapping[chosen[0]], partner_call.bid.level, current_bid)
            if bid is not None:
                return Call(player, CallType.BID, bid)

        return Call(player, CallType.PASS)

    def _suggest_overcall_call(
        self,
        player: BridgePlayer,
        hcp: int,
        distribution: Counter[Suit],
        current_bid: Optional[Bid],
    ) -> Call:
        """Suggest an action after an opponent bid."""

        if current_bid is None:
            return Call(player, CallType.PASS)

        if hcp >= 15 and self._is_balanced(distribution):
            bid = self._construct_bid(BidSuit.NO_TRUMP, max(1, current_bid.level), current_bid)
            if bid is not None and bid.level <= 3:
                return Call(player, CallType.BID, bid)

        if hcp >= 12:
            suits = [(suit, count) for suit, count in distribution.items() if count >= 5]
            if suits:
                mapping = {
                    Suit.CLUBS: BidSuit.CLUBS,
                    Suit.DIAMONDS: BidSuit.DIAMONDS,
                    Suit.HEARTS: BidSuit.HEARTS,
                    Suit.SPADES: BidSuit.SPADES,
                }
                chosen = max(suits, key=lambda item: (item[1], mapping[item[0]].value))
                bid = self._construct_bid(mapping[chosen[0]], current_bid.level, current_bid)
                if bid is not None:
                    return Call(player, CallType.BID, bid)

        return Call(player, CallType.PASS)

    def _consider_double_call(
        self,
        player: BridgePlayer,
        hcp: int,
        history: list[Call],
        last_bid: Optional[Call],
    ) -> Optional[Call]:
        """Return a takeout double when conditions merit it."""

        if last_bid is None or last_bid.bid is None:
            return None

        partnership = self.partnership_for(player)
        last_partnership = self.partnership_for(last_bid.player)
        if partnership == last_partnership:
            return None

        for call in reversed(history):
            if call.call_type == CallType.BID:
                break
            if call.call_type == CallType.DOUBLE and self.partnership_for(call.player) == partnership:
                return None

        if hcp >= 15 and last_bid.bid.level >= 3:
            return Call(player, CallType.DOUBLE)

        return None

    def suggest_call(self, player: BridgePlayer, history: list[Call]) -> Call:
        """Suggest a bidding call for a player.

        Args:
            player: The active player considering a call.
            history: The calls that have been made so far in the auction.

        Returns:
            The call that the AI would make for the player.
        """

        hcp = self.evaluate_hand(player)
        distribution = self._hand_distribution(player.hand)
        current_bid = self._current_highest_bid(history)
        last_non_pass = self._last_non_pass_call(history)

        if last_non_pass is None:
            return self._suggest_opening_call(player, hcp, distribution, current_bid)

        if last_non_pass.call_type in {CallType.DOUBLE, CallType.REDOUBLE}:
            return Call(player, CallType.PASS)

        if self.partnership_for(last_non_pass.player) == self.partnership_for(player):
            return self._suggest_response_call(player, hcp, distribution, last_non_pass, current_bid)

        double_call = self._consider_double_call(player, hcp, history, last_non_pass)
        if double_call is not None:
            return double_call

        return self._suggest_overcall_call(player, hcp, distribution, current_bid)

    def conduct_bidding(self) -> Optional[Contract]:
        """Conduct the auction and establish the final contract.

        Returns:
            The resulting contract if a bid is made, otherwise ``None`` when
            the board is passed out.
        """

        history: list[Call] = []
        passes_in_row = 0
        player_index = self.dealer_index
        current_bid: Optional[Bid] = None
        current_bidder: Optional[BridgePlayer] = None
        doubled = False
        redoubled = False
        first_bidder_by_partnership: dict[tuple[str, BidSuit], BridgePlayer] = {}

        while True:
            player = self.players[player_index]
            call = self.suggest_call(player, history.copy())

            if call.call_type == CallType.BID and call.bid is not None:
                if call.bid.level < 1 or call.bid.level > 7:
                    call = Call(player, CallType.PASS)
                elif current_bid is not None and call.bid.score() <= current_bid.score():
                    call = Call(player, CallType.PASS)

            if call.call_type == CallType.BID and call.bid is not None:
                current_bid = call.bid
                current_bidder = player
                passes_in_row = 0
                doubled = False
                redoubled = False
                partnership = self.partnership_for(player)
                first_bidder_by_partnership.setdefault((partnership, call.bid.suit), player)
            elif call.call_type == CallType.DOUBLE and current_bidder is not None:
                if self.partnership_for(player) == self.partnership_for(current_bidder) or doubled:
                    call = Call(player, CallType.PASS)
                    passes_in_row += 1
                else:
                    doubled = True
                    redoubled = False
                    passes_in_row = 0
            elif call.call_type == CallType.REDOUBLE and current_bidder is not None:
                if not doubled or self.partnership_for(player) != self.partnership_for(current_bidder):
                    call = Call(player, CallType.PASS)
                    passes_in_row += 1
                else:
                    redoubled = True
                    passes_in_row = 0
            else:
                passes_in_row += 1

            history.append(call)
            player_index = (player_index + 1) % 4

            if current_bid is None and passes_in_row >= 4:
                self.bidding_history = history
                self.contract = None
                return None

            if current_bid is not None and passes_in_row >= 3:
                break

        self.bidding_history = history

        if current_bid is None or current_bidder is None:
            self.contract = None
            return None

        partnership = self.partnership_for(current_bidder)
        declarer = first_bidder_by_partnership.get((partnership, current_bid.suit), current_bidder)
        self.declarer_index = self.players.index(declarer)

        trump_suit = self._bid_suit_to_card_suit(current_bid.suit)
        self.trump_suit = trump_suit
        self.contract = Contract(current_bid, declarer, doubled=doubled, redoubled=redoubled)
        return self.contract

    # ------------------------------------------------------------------
    # Play
    # ------------------------------------------------------------------
    def is_valid_play(self, player: BridgePlayer, card: Card) -> bool:
        """Determine whether a card play is legal.

        Args:
            player: The player attempting to play the card.
            card: The card under consideration.

        Returns:
            ``True`` if the card can legally be played, otherwise ``False``.
        """

        if card not in player.hand:
            return False
        if not self.current_trick:
            return True
        if self.lead_suit is None:
            return True
        if any(hand_card.suit == self.lead_suit for hand_card in player.hand):
            return card.suit == self.lead_suit
        return True

    def play_card(self, player: BridgePlayer, card: Card) -> None:
        """Play a card into the current trick.

        Args:
            player: The player playing the card.
            card: The card to place into the current trick.

        Raises:
            ValueError: If the attempted play is illegal.
        """

        if not self.is_valid_play(player, card):
            raise ValueError("Invalid play")
        player.hand.remove(card)
        self.current_trick.append((player, card))
        if len(self.current_trick) == 1:
            self.lead_suit = card.suit

    def _is_better_card(self, candidate: Card, current: Card, lead_suit: Suit) -> bool:
        """Return whether ``candidate`` wins against ``current`` given context."""

        if self.trump_suit is not None:
            if candidate.suit == self.trump_suit and current.suit != self.trump_suit:
                return True
            if current.suit == self.trump_suit and candidate.suit != self.trump_suit:
                return False
        if candidate.suit == current.suit:
            return candidate.value > current.value
        if candidate.suit == lead_suit and current.suit != lead_suit:
            return True
        return False

    def _evaluate_trick_winner(self) -> tuple[BridgePlayer, Card]:
        """Return the provisional winner of the current trick."""

        winner, winning_card = self.current_trick[0]
        lead_suit = self.current_trick[0][1].suit
        for contender, card in self.current_trick[1:]:
            if self._is_better_card(card, winning_card, lead_suit):
                winner, winning_card = contender, card
        return winner, winning_card

    def complete_trick(self) -> BridgePlayer:
        """Resolve the current trick and return the winning player."""

        if len(self.current_trick) != 4:
            raise RuntimeError("Trick is not complete")
        winner, _ = self._evaluate_trick_winner()
        winner.tricks_won += 1
        self.current_trick = []
        self.lead_suit = None
        return winner

    def get_valid_plays(self, player: BridgePlayer) -> list[Card]:
        """Return all legal plays for a player.

        Args:
            player: The player whose options are requested.

        Returns:
            A list of cards that may legally be played.
        """

        return [card for card in player.hand if self.is_valid_play(player, card)]

    def _lead_card_strategy(self, player: BridgePlayer, valid_cards: list[Card]) -> Card:
        """Select a leading card using a simple heuristic."""

        distribution = self._hand_distribution(valid_cards)
        ordered_suits = sorted(
            distribution.items(),
            key=lambda item: (-item[1], SUIT_ORDER[item[0]]),
        )
        for suit, _ in ordered_suits:
            suit_cards = [card for card in valid_cards if card.suit == suit]
            if suit_cards:
                return max(suit_cards, key=lambda card: card.value)
        return max(valid_cards, key=lambda card: card.value)

    def _follow_card_strategy(self, player: BridgePlayer, valid_cards: list[Card]) -> Card:
        """Select a card when following to a trick."""

        winner, winning_card = self._evaluate_trick_winner()
        lead_suit = self.current_trick[0][1].suit
        partnership = self.partnership_for(player)
        partner_winning = self.partnership_for(winner) == partnership

        suit_cards = [card for card in valid_cards if card.suit == lead_suit]
        if suit_cards:
            suit_cards.sort(key=lambda card: card.value)
            if partner_winning:
                return suit_cards[0]
            beating_cards = [card for card in suit_cards if card.value > winning_card.value]
            if beating_cards:
                return beating_cards[0]
            return suit_cards[0]

        if self.trump_suit is not None:
            trump_cards = [card for card in valid_cards if card.suit == self.trump_suit]
            if trump_cards:
                trump_cards.sort(key=lambda card: card.value)
                if winning_card.suit == self.trump_suit:
                    beating_trumps = [card for card in trump_cards if card.value > winning_card.value]
                    if beating_trumps and not partner_winning:
                        return beating_trumps[0]
                    if partner_winning:
                        non_trump_discards = [card for card in valid_cards if card.suit != self.trump_suit]
                        if non_trump_discards:
                            return min(non_trump_discards, key=lambda card: card.value)
                    return trump_cards[0]
                if not partner_winning:
                    return trump_cards[0]

        return min(valid_cards, key=lambda card: card.value)

    def select_card_to_play(self, player: BridgePlayer) -> Card:
        """Select a card for an AI player to play.

        Args:
            player: The AI-controlled player.

        Returns:
            The card chosen according to the AI heuristic.

        Raises:
            RuntimeError: If no valid cards are available.
        """

        valid_cards = self.get_valid_plays(player)
        if not valid_cards:
            raise RuntimeError("Player has no valid cards")
        if len(valid_cards) == 1:
            return valid_cards[0]
        if not self.current_trick:
            return self._lead_card_strategy(player, valid_cards)
        return self._follow_card_strategy(player, valid_cards)

    def starting_player_index(self) -> int:
        """Return the index of the opening leader for the hand.

        Returns:
            The player index of the left-hand opponent of declarer.
        """

        if self.declarer_index is None:
            return 0
        return (self.declarer_index + 1) % 4

    # ------------------------------------------------------------------
    # Scoring
    # ------------------------------------------------------------------
    def _is_vulnerable(self, partnership: str) -> bool:
        """Return whether ``partnership`` is vulnerable."""

        if self.vulnerability == Vulnerability.BOTH:
            return True
        if self.vulnerability == Vulnerability.NONE:
            return False
        if self.vulnerability == Vulnerability.NORTH_SOUTH:
            return partnership == "NS"
        return partnership == "EW"

    def _trick_score(self, bid: Bid, doubled: bool, redoubled: bool) -> int:
        """Compute trick score for a contract."""

        if bid.suit == BidSuit.NO_TRUMP:
            base = 40 + (bid.level - 1) * 30
        elif bid.suit in {BidSuit.HEARTS, BidSuit.SPADES}:
            base = bid.level * 30
        else:
            base = bid.level * 20

        multiplier = 1
        if redoubled:
            multiplier = 4
        elif doubled:
            multiplier = 2
        return base * multiplier

    def _made_contract_score(
        self,
        tricks_won: int,
        bid: Bid,
        partnership: str,
        doubled: bool,
        redoubled: bool,
    ) -> int:
        """Return declarer partnership score for a made contract."""

        vulnerable = self._is_vulnerable(partnership)
        required = 6 + bid.level
        overtricks = tricks_won - required
        trick_points = self._trick_score(bid, doubled, redoubled)

        bonus = 0
        if redoubled:
            bonus += 100
        elif doubled:
            bonus += 50

        if trick_points >= 100:
            bonus += 500 if vulnerable else 300
        else:
            bonus += 50

        if bid.level == 6:
            bonus += 750 if vulnerable else 500
        elif bid.level == 7:
            bonus += 1500 if vulnerable else 1000

        if overtricks > 0:
            if redoubled:
                bonus += overtricks * (400 if vulnerable else 200)
            elif doubled:
                bonus += overtricks * (200 if vulnerable else 100)
            else:
                if bid.suit in {BidSuit.HEARTS, BidSuit.SPADES, BidSuit.NO_TRUMP}:
                    bonus += overtricks * 30
                else:
                    bonus += overtricks * 20

        return trick_points + bonus

    def _failed_contract_penalty(
        self,
        tricks_won: int,
        bid: Bid,
        partnership: str,
        doubled: bool,
        redoubled: bool,
    ) -> int:
        """Return defenders' penalty score."""

        vulnerable = self._is_vulnerable(partnership)
        required = 6 + bid.level
        undertricks = required - tricks_won

        if not doubled and not redoubled:
            penalty = undertricks * (100 if vulnerable else 50)
            return penalty

        penalties: list[int] = []
        for index in range(undertricks):
            if vulnerable:
                penalty_value = 200 if index == 0 else 300
            else:
                if index == 0:
                    penalty_value = 100
                elif index in {1, 2}:
                    penalty_value = 200
                else:
                    penalty_value = 300
            penalties.append(penalty_value)

        multiplier = 2 if redoubled else 1
        return sum(penalties) * multiplier

    def calculate_score(self) -> dict[str, int]:
        """Return rubber-style scores for both partnerships.

        Returns:
            A mapping of partnership identifiers to their scores.
        """

        if self.contract is None:
            return {"north_south": 0, "east_west": 0}

        declarer = self.contract.declarer
        partner = self.players[declarer.partner_index]
        tricks_won = declarer.tricks_won + partner.tricks_won
        partnership = self.partnership_for(declarer)
        required = 6 + self.contract.bid.level
        if tricks_won >= required:
            declarer_score = self._made_contract_score(
                tricks_won,
                self.contract.bid,
                partnership,
                self.contract.doubled,
                self.contract.redoubled,
            )
            defender_score = 0
        else:
            declarer_score = 0
            defender_score = self._failed_contract_penalty(
                tricks_won,
                self.contract.bid,
                partnership,
                self.contract.doubled,
                self.contract.redoubled,
            )

        scores = {"north_south": 0, "east_west": 0}
        if partnership == "NS":
            scores["north_south"] = declarer_score
            scores["east_west"] = defender_score
        else:
            scores["east_west"] = declarer_score
            scores["north_south"] = defender_score
        return scores
