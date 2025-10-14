"""Command-line interface for the Cribbage card game."""

from __future__ import annotations

from typing import Optional

from card_games.common.cards import Card
from card_games.cribbage.game import CribbageGame, GamePhase


def display_hand(cards: list[Card], player: str) -> None:
    """Display a player's hand.

    Args:
        cards: The cards to display
        player: Player name
    """
    if not cards:
        print(f"{player} has no cards left.")
        return

    print(f"\n{player}'s hand:")
    for i, card in enumerate(cards, 1):
        print(f"  {i}. {card}")


def display_game_state(game: CribbageGame) -> None:
    """Display the current game state.

    Args:
        game: The Cribbage game instance
    """
    state = game.get_state_summary()
    print("\n" + "=" * 60)
    print(f"CRIBBAGE - {state['phase']}")
    print("=" * 60)
    print(f"Player 1: {state['player1_score']} points ({state['player1_cards']} cards)")
    print(f"Player 2: {state['player2_score']} points ({state['player2_cards']} cards)")
    print(f"Dealer: Player {state['dealer']}")
    if state["starter"]:
        print(f"Starter: {state['starter']}")
    if state["phase"] == "PLAY":
        print(f"Count: {state['play_count']}")
        print(f"Current player: Player {state['current_player']}")
    print("=" * 60)


def get_card_choice(hand: list[Card], prompt: str) -> Optional[Card]:
    """Get a card choice from the player.

    Args:
        hand: Player's hand
        prompt: Prompt message

    Returns:
        Selected card or None
    """
    while True:
        try:
            choice = input(prompt).strip()
            if not choice:
                return None
            idx = int(choice) - 1
            if 0 <= idx < len(hand):
                return hand[idx]
            print("Invalid choice. Try again.")
        except (ValueError, IndexError):
            print("Invalid input. Enter a number.")


def game_loop(game: CribbageGame) -> None:
    """Main game loop for CLI.

    Args:
        game: The Cribbage game instance
    """
    print("\n🎴 Welcome to Cribbage! 🎴")
    print("First to 121 points wins!")
    print("\nNote: This is a simplified version focusing on scoring.")
    print("For a full experience with strategy and AI, try the GUI version.\n")

    while game.phase != GamePhase.GAME_OVER:
        display_game_state(game)

        if game.phase == GamePhase.DISCARD:
            # Player 1 discards
            display_hand(game.player1_hand, "Player 1")
            print("\nSelect 2 cards to discard to the crib:")
            discards = []
            for i in range(2):
                card = get_card_choice(game.player1_hand, f"Card {i+1} (1-{len(game.player1_hand)}): ")
                if card:
                    discards.append(card)
                else:
                    print("Invalid selection.")
                    continue

            if len(discards) == 2:
                game.discard_to_crib(1, discards)

            # Player 2 discards (simulated - random selection)
            if len(game.crib) < 4 and len(game.player2_hand) >= 2:
                import random

                p2_discards = random.sample(game.player2_hand, 2)
                game.discard_to_crib(2, p2_discards)
                print("\nPlayer 2 discards to crib.")

        elif game.phase == GamePhase.PLAY:
            if game.current_player == 1:
                display_hand(game.player1_hand, "Player 1")

                # Check if player can play any card
                can_play = any(game.can_play_card(1, card) for card in game.player1_hand)

                if not can_play:
                    print("\nPlayer 1 says 'Go' (cannot play)")
                    game.current_player = 2
                    continue

                card = get_card_choice(game.player1_hand, "\nChoose a card to play (1-4): ")
                if card:
                    result = game.play_card(1, card)
                    if result["success"]:
                        print(f"\nPlayer 1 plays {card}")
                        print(f"Count: {result['count']}")
                        if result["points"] > 0:
                            print(f"🎉 Scored {result['points']} points!")
                    else:
                        print("Cannot play that card!")
            else:
                # Player 2 plays (simulated)
                playable = [card for card in game.player2_hand if game.can_play_card(2, card)]

                if not playable:
                    print("\nPlayer 2 says 'Go' (cannot play)")
                    game.current_player = 1
                    continue

                card = playable[0]  # Simple AI: play first playable card
                result = game.play_card(2, card)
                if result["success"]:
                    print(f"\nPlayer 2 plays {card}")
                    print(f"Count: {result['count']}")
                    if result["points"] > 0:
                        print(f"Player 2 scored {result['points']} points!")

        elif game.phase == GamePhase.SHOW:
            print("\n" + "=" * 60)
            print("THE SHOW - Scoring Hands")
            print("=" * 60)

            # Score player 1's hand
            p1_points = game.score_hand(game.player1_hand)
            game.player1_score += p1_points
            print(f"\nPlayer 1's hand scores: {p1_points} points")

            # Score player 2's hand
            p2_points = game.score_hand(game.player2_hand)
            game.player2_score += p2_points
            print(f"Player 2's hand scores: {p2_points} points")

            # Score crib (dealer gets these points)
            crib_points = game.score_hand(game.crib, is_crib=True)
            if game.dealer == 1:
                game.player1_score += crib_points
                print(f"\nCrib (Player 1's) scores: {crib_points} points")
            else:
                game.player2_score += crib_points
                print(f"\nCrib (Player 2's) scores: {crib_points} points")

            # Check for winner
            if game.player1_score >= 121:
                game.winner = 1
                game.phase = GamePhase.GAME_OVER
            elif game.player2_score >= 121:
                game.winner = 2
                game.phase = GamePhase.GAME_OVER
            else:
                # Start new hand
                game.dealer = 2 if game.dealer == 1 else 1
                game.__init__()

            input("\nPress Enter to continue...")

    # Game over
    print("\n" + "=" * 60)
    print("GAME OVER")
    print("=" * 60)
    if game.winner:
        print(f"🎉 Player {game.winner} wins!")
        print(f"Final Score: Player 1: {game.player1_score}, Player 2: {game.player2_score}")
    print("=" * 60)
