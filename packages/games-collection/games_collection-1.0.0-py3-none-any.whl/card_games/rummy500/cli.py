"""Command-line interface for Rummy 500."""

from __future__ import annotations

from card_games.rummy500.game import GamePhase, Rummy500Game


def display_game_state(game: Rummy500Game) -> None:
    """Display current game state."""
    state = game.get_state_summary()
    print("\n" + "=" * 60)
    print(f"RUMMY 500 - {state['phase']}")
    print("=" * 60)
    for i, score in enumerate(state["scores"]):
        marker = " <--" if i == state["current_player"] else ""
        print(f"Player {i}: {score} points ({state['hand_sizes'][i]} cards){marker}")
    if state["discard_top"]:
        print(f"Top of discard: {state['discard_top']}")
    print(f"Deck: {state['deck_size']} cards")
    print("=" * 60)


def game_loop(game: Rummy500Game) -> None:
    """Main game loop."""
    print("\n🃏 Welcome to Rummy 500! 🃏")
    print(f"{game.num_players} players - First to 500 points wins!")
    print("\nNote: This is a simplified version.")
    print("Full meld rules and AI strategy planned for future updates.\n")

    while game.phase != GamePhase.GAME_OVER:
        display_game_state(game)

        player = game.current_player

        if game.phase == GamePhase.DRAW:
            if player == 0:
                # Human player
                print(f"\nPlayer {player}'s turn")
                choice = input("Draw from (d)eck or (p)ile? [d]: ").strip().lower()
                game.draw_card(from_discard=(choice == "p"))
            else:
                # AI player
                game.draw_card()
                print(f"Player {player} draws a card")

        if game.phase == GamePhase.MELD:
            # Simplified: skip meld phase for now
            if player == 0:
                print(f"\nYour hand: {', '.join(str(c) for c in game.hands[player])}")
                input("Press Enter to discard...")

            # Discard
            if game.hands[player]:
                card = game.hands[player][0]  # Simplified: discard first card
                game.discard(player, card)
                if player == 0:
                    print(f"You discard {card}")

    # Game over
    state = game.get_state_summary()
    print("\n" + "=" * 60)
    print("GAME OVER")
    print("=" * 60)
    print(f"🎉 Player {state['winner']} wins!")
    print("\nFinal Scores:")
    for i, score in enumerate(state["scores"]):
        print(f"  Player {i}: {score} points")
    print("=" * 60)
