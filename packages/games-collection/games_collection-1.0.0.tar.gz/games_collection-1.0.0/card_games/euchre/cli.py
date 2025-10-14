"""Command-line interface for the Euchre card game."""

from __future__ import annotations

from card_games.euchre.game import EuchreGame, GamePhase


def display_game_state(game: EuchreGame) -> None:
    """Display current game state."""
    state = game.get_state_summary()
    print("\n" + "=" * 60)
    print(f"EUCHRE - {state['phase']}")
    print("=" * 60)
    print(f"Team 1 (Players 0&2): {state['team1_score']} points")
    print(f"Team 2 (Players 1&3): {state['team2_score']} points")
    print(f"Dealer: Player {state['dealer']}")
    if state["trump"]:
        print(f"Trump: {state['trump']}")
        print(f"Maker: Team {state['maker']}")
    print(f"Current player: Player {state['current_player']}")
    print("=" * 60)


def game_loop(game: EuchreGame) -> None:
    """Main game loop for CLI."""
    print("\n🂡 Welcome to Euchre! 🂡")
    print("Four players in partnerships: Team 1 (0&2) vs Team 2 (1&3)")
    print("First to 10 points wins!\n")

    while game.phase != GamePhase.GAME_OVER:
        display_game_state(game)

        if game.phase == GamePhase.BIDDING:
            print("\nBidding Phase")
            print("Player 0 selects trump (simplified)...")
            # Simplified: First player after dealer picks trump
            if game.hands[0]:
                trump_suit = game.hands[0][0].suit
                game.select_trump(trump_suit, 0)
                print(f"Trump selected: {trump_suit}")

        elif game.phase == GamePhase.PLAY:
            player = game.current_player
            print(f"\nPlayer {player}'s turn")
            print(f"Hand: {', '.join(str(c) for c in game.hands[player])}")

            if player == 0:
                # Human player
                if game.hands[player]:
                    card = game.hands[player][0]  # Simplified: play first card
                    result = game.play_card(player, card)
                    if result["success"]:
                        print(f"Player {player} plays {card}")
            else:
                # AI players (simplified: play first card)
                if game.hands[player]:
                    card = game.hands[player][0]
                    result = game.play_card(player, card)
                    if result["success"]:
                        print(f"Player {player} plays {card}")

            input("Press Enter to continue...")

    # Game over
    state = game.get_state_summary()
    print("\n" + "=" * 60)
    print("GAME OVER")
    print("=" * 60)
    print(f"🎉 Team {state['winner']} wins!")
    print(f"Final Score: Team 1: {state['team1_score']}, Team 2: {state['team2_score']}")
    print("=" * 60)
