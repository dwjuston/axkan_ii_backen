from dice import DiceCollectionType
from game_context import GameContext
from game_manager import GameManager
from player import Player
from enums import GamePhase, GameAction
from card import Card, CardPair, CardSuit, CardRank, CardType


def test_simple_game_flow():
    # Initialize game
    manager = GameManager(use_cli=False)  # Disable CLI

    # Create players
    p1 = Player(player_id="Player 1")
    p2 = Player(player_id="Player 2")

    # Add players to game
    manager.add_player(p1)
    manager.add_player(p2)

    # Start the game
    manager.start_game()

    # GAME_INIT phase
    assert manager.context.current_phase == GamePhase.GAME_INIT
    manager.initialize_game()
    manager.roll_dice()

    # Play 7 turns
    for turn in range(1, 8):
        manager.start_turn()
        assert manager.context.current_phase == GamePhase.TURN_SELECT_FIRST

        # First selector chooses
        first_player = manager.context.first_selector
        manager.select_pair(0)
        assert len(manager.context.selected_pairs) == 1
        assert manager.context.selected_pairs[0] in first_player.selected_pairs
        assert len(manager.context.available_pairs) == 2
        assert manager.context.current_phase == GamePhase.TURN_SELECT_SECOND

        # Second selector chooses
        second_player = manager.context.second_selector
        manager.select_pair(1)
        assert len(manager.context.selected_pairs) == 2
        assert manager.context.selected_pairs[1] in second_player.selected_pairs
        assert len(manager.context.available_pairs) == 1
        assert manager.context.current_phase == GamePhase.TURN_COMPLETE


        # Roll dice
        dice_roller = manager.context.dice_roller
        dice_type = DiceCollectionType.REGULAR
        manager.roll_dice(dice_type)
        assert manager.context.current_phase == GamePhase.TURN_START

    # Turn 8
    manager.start_turn()

    # FINAL_REVIEW phase
    assert manager.context.current_phase == GamePhase.FINAL_REVIEW

    # Players can use seven cards
    for player in manager.context.players:
        if player.portfolio.has_seven_card():
            if player == manager.context.players[0]:  # P1 converts selected pair
                special_card_index = 0
                player.convert_card_color(player.selected_pairs[0], special_card_index)
            else:  # P2 converts hidden pair
                special_card_index = 0
                player.convert_card_color(player.hidden_pairs[0], special_card_index)

    # GAME_END phase
    manager.end_review()
    assert manager.context.current_phase == GamePhase.GAME_END
    # Calculate final scores
    for player in manager.context.players:
        player.recalculate_score(manager.context.current_price)
