"""Command-line interface for Bridge."""

from __future__ import annotations

import random
from typing import Optional

from card_games.bridge.game import BidSuit, BridgeGame, BridgePlayer, CallType, Vulnerability
from card_games.common.cards import format_cards, parse_card

SUIT_SYMBOLS = {
    BidSuit.CLUBS: "♣",
    BidSuit.DIAMONDS: "♦",
    BidSuit.HEARTS: "♥",
    BidSuit.SPADES: "♠",
    BidSuit.NO_TRUMP: "NT",
}


def display_hand(player: BridgePlayer) -> None:
    """Display a player's hand.

    Args:
        player: The player whose hand should be printed.
    """

    print(f"\n{player.name} ({player.position}): {format_cards(player.hand)}")


def format_call(
    player: BridgePlayer,
    call_type: CallType,
    bid: Optional[BidSuit],
    level: Optional[int],
) -> str:
    """Return a printable representation of a call.

    Args:
        player: The player who made the call.
        call_type: The type of call made during the auction.
        bid: The bid suit if the call was a bid.
        level: The level associated with the bid.

    Returns:
        A formatted string describing the call.
    """

    if call_type == CallType.BID and bid is not None and level is not None:
        return f"{player.position}: {level}{SUIT_SYMBOLS[bid]}"
    if call_type == CallType.DOUBLE:
        return f"{player.position}: X"
    if call_type == CallType.REDOUBLE:
        return f"{player.position}: XX"
    return f"{player.position}: Pass"


def game_loop() -> None:
    """Run the interactive loop for a single bridge deal."""

    print("\nWELCOME TO BRIDGE")
    print("=" * 60)
    print("Contract Bridge with realistic bidding, vulnerability, and scoring.")
    print("=" * 60)

    player_name = input("\nEnter your name (you are South): ").strip() or "Player"

    players = [
        BridgePlayer(name="North AI", is_ai=True),
        BridgePlayer(name=f"South {player_name}", is_ai=False),
        BridgePlayer(name="East AI", is_ai=True),
        BridgePlayer(name="West AI", is_ai=True),
    ]

    vulnerability = random.choice(list(Vulnerability))
    game = BridgeGame(players, vulnerability=vulnerability)

    print("\n" + "=" * 60)
    print("DEALING CARDS")
    print("=" * 60)
    print(f"Vulnerability: {game.vulnerability.value}")

    game.deal_cards()

    for player in players:
        if not player.is_ai:
            display_hand(player)
            hcp = game.evaluate_hand(player)
            print(f"High Card Points: {hcp}")

    print("\n" + "=" * 60)
    print("BIDDING PHASE")
    print("=" * 60)
    print("(Automated bidding)")

    contract = game.conduct_bidding()

    if contract is None:
        print("\nAll players passed. No contract for this deal.")
        return

    print("\nBidding sequence:")
    for call in game.bidding_history:
        bid = call.bid.suit if call.bid else None
        level = call.bid.level if call.bid else None
        print(f"  {format_call(call.player, call.call_type, bid, level)}")

    declarer = contract.declarer
    dummy = game.players[declarer.partner_index]
    contract_str = f"{contract.bid.level}{SUIT_SYMBOLS[contract.bid.suit]}"
    if contract.doubled:
        contract_str += " X"
    if contract.redoubled:
        contract_str += " XX"

    print(f"\nContract: {contract_str} by {declarer.name} ({declarer.position})")
    print(f"Dummy: {dummy.name} ({dummy.position})")

    print("\n" + "=" * 60)
    print("PLAYING PHASE")
    print("=" * 60)

    opening_leader_index = game.starting_player_index()
    current_player_idx = opening_leader_index
    dummy_revealed = False

    for trick_num in range(13):
        print(f"\n--- Trick {trick_num + 1} ---")

        for i in range(4):
            player = game.players[(current_player_idx + i) % 4]

            if player.is_ai:
                card = game.select_card_to_play(player)
            else:
                display_hand(player)
                print("\nCurrent trick:")
                for played_player, played_card in game.current_trick:
                    print(f"  {played_player.position}: {played_card}")

                valid_cards = game.get_valid_plays(player)
                print(f"\nValid cards: {format_cards(valid_cards)}")

                while True:
                    try:
                        card_code = input("Enter card to play: ").strip().upper()
                        card = parse_card(card_code)
                        if card in valid_cards:
                            break
                        print("Invalid play")
                    except (ValueError, KeyError):
                        print("Invalid card")

            game.play_card(player, card)
            print(f"{player.position} plays {card}")

            if not dummy_revealed and game.players.index(player) == opening_leader_index:
                dummy_revealed = True
                if dummy.is_ai:
                    display_hand(dummy)

        winner = game.complete_trick()
        print(f"{winner.position} wins the trick")
        current_player_idx = game.players.index(winner)

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)

    partner = game.players[declarer.partner_index]
    declarer_tricks = declarer.tricks_won + partner.tricks_won
    defender_tricks = 13 - declarer_tricks

    print(f"\nDeclarer partnership ({declarer.position}-{partner.position}): {declarer_tricks} tricks")
    print(f"Defender partnership: {defender_tricks} tricks")

    required = 6 + contract.bid.level
    print(f"\nContract required: {required} tricks")

    scores = game.calculate_score()
    if declarer_tricks >= required:
        print(f"✓ Contract MADE by {declarer.position}")
    else:
        print("✗ Contract FAILED")

    print(
        "Score summary - North/South: {north_south} | East/West: {east_west}".format(
            **scores,
        )
    )
