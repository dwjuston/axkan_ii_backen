from enums import GamePhase
from game_context import GameContext, GameResult
from player import Player


def test_game_context_start():
    # Lobby => Game Start
    context = GameContext()
    assert context.current_phase == GamePhase.LOBBY

    player1 = Player(uuid="1", player_id=0, name="Player 1")
    player2 = Player(uuid="2", player_id=1, name="Player 2")
    context.add_player(player1)
    context.add_player(player2)
    board_for_player1 = context.create_board(player1.player_id)
    assert board_for_player1.current_phase == GamePhase.GAME_START
    assert board_for_player1.turn_number == 1
    assert board_for_player1.dice_result == []
    assert board_for_player1.dice_extra == 0
    assert board_for_player1.stock_price is None
    assert board_for_player1.current_player.player_id == player1.player_id
    assert board_for_player1.opponent.player_id == player2.player_id

    # Game Start => Game Init
    context.initialize_game()
    board_for_player2 = context.create_board(player2.player_id)
    assert board_for_player2.current_phase == GamePhase.GAME_INIT
    assert board_for_player2.turn_number == 1
    assert board_for_player2.current_player.player_id == player2.player_id
    assert board_for_player2.opponent.player_id == player1.player_id
    assert board_for_player2.current_player.hidden_pair is not None
    assert len(board_for_player2.current_player.seven_cards) == 2
    assert  board_for_player2.current_player.selected_pairs == []

    # Game Init => Turn Start
    context.roll_dice()
    board_for_player1 = context.create_board(player1.player_id)
    assert board_for_player1.current_phase == GamePhase.TURN_START
    assert board_for_player1.turn_number == 1
    assert len(board_for_player1.dice_result) == 1
    assert board_for_player1.dice_extra == 0
    assert board_for_player1.stock_price is not None
    assert board_for_player1.current_player.player_id == player1.player_id
    assert board_for_player1.opponent.player_id == player2.player_id

    # Turn Start => Turn Select First
    context.start_turn()
    board_for_player2 = context.create_board(player2.player_id)
    assert board_for_player2.current_phase == GamePhase.TURN_SELECT_FIRST
    assert board_for_player2.first_selector is not None
    assert board_for_player2.second_selector is not None
    assert board_for_player2.dice_roller == board_for_player2.second_selector
    assert len(board_for_player2.available_pairs) == 3
    assert board_for_player2.selected_pair_index == {}


def test_game_context_turn():
    context = GameContext()
    player1 = Player(uuid="1", player_id=0, name="Player 1")
    player2 = Player(uuid="2", player_id=1, name="Player 2")
    context.add_player(player1)
    context.add_player(player2)
    context.initialize_game()
    context.roll_dice()

    # Turn Start => Turn Select First
    context.start_turn()
    board_for_player1 = context.create_board(0)
    assert board_for_player1.current_phase == GamePhase.TURN_SELECT_FIRST

    assert board_for_player1.first_selector == 0
    assert board_for_player1.second_selector == 1
    assert board_for_player1.dice_roller == 1

    # Turn Select First => Turn Select Second
    pair = board_for_player1.available_pairs[0]
    context.select_pair(pair)
    board2 = context.create_board(1)
    assert board2.current_phase == GamePhase.TURN_SELECT_SECOND
    assert board2.first_selector == 0
    assert board2.second_selector == 1
    assert board2.dice_roller == 1
    assert len(board2.selected_pair_index) == 1

    # Turn Select Second => Turn Complete
    pair2 = board2.available_pairs[1]
    context.select_pair(pair2)
    board1 = context.create_board(0)
    assert board1.current_phase == GamePhase.TURN_COMPLETE

    assert board1.current_player.selected_pairs == [pair]
    assert board1.opponent.selected_pairs == [pair2]

    # Turn Complete => Turn Start
    context.roll_dice()
    board1 = context.create_board(player1.player_id)
    assert board1.current_phase == GamePhase.TURN_START
    assert board1.turn_number == 2

    # Turn 2: Turn Start => Turn Select First
    context.start_turn()
    board1 = context.create_board(player1.player_id)
    assert board1.current_phase == GamePhase.TURN_SELECT_FIRST
    assert board1.first_selector == 1
    assert board1.second_selector == 0
    assert board1.dice_roller == 0
    assert len(board1.available_pairs) == 3
    assert board1.selected_pair_index == {}

def test_game_context_end():
    context = GameContext()
    player1 = Player(uuid="1", player_id=0, name="Player 1")
    player2 = Player(uuid="2", player_id=1, name="Player 2")
    context.add_player(player1)
    context.add_player(player2)
    context.initialize_game()
    context.roll_dice()

    for i in range(7):
        context.start_turn()
        context.select_pair(context.available_pairs[0])
        context.select_pair(context.available_pairs[1])
        context.roll_dice()

    # Turn 8
    board_for_player1 = context.create_board(0)
    assert board_for_player1.current_phase == GamePhase.FINAL_REVIEW
    assert board_for_player1.turn_number == 7
    assert len(board_for_player1.current_player.selected_pairs) == 7
    assert len(board_for_player1.opponent.selected_pairs) == 7

    # convert color
    context.convert_color(player_id=0, pair_index=0, special_card_index=0)
    assert len(context.player_1.seven_cards) == 1
    context.convert_color(player_id=0, pair_index=1, special_card_index=0)
    assert len(context.player_1.seven_cards) == 0

    context.convert_color(player_id=1, pair_index=1, special_card_index=1)
    assert len(context.player_2.seven_cards) == 1
    context.convert_color(player_id=1, pair_index=-1, special_card_index=0)
    assert len(context.player_2.seven_cards) == 0


    # Final Review => Game End
    context.end_review()
    board_for_player1 = context.create_board(0)
    board_for_player2 = context.create_board(1)
    assert board_for_player1.current_phase == GamePhase.GAME_END

    final_result = context.calculate_final_results()
    assert isinstance(final_result, GameResult)
    assert board_for_player1.current_player == final_result.player_1
    assert board_for_player2.current_player == final_result.player_2

    # Game End => Lobby
    context.initialize_game()
    board_for_player1 = context.create_board(0)
    assert board_for_player1.current_phase == GamePhase.GAME_INIT
    assert board_for_player1.turn_number == 1
    assert board_for_player1.dice_result == []
    assert board_for_player1.dice_extra == 0
    assert board_for_player1.stock_price is None
    assert board_for_player1.current_player.player_id == 0
    assert board_for_player1.opponent.player_id == 1
    assert board_for_player1.current_player.selected_pairs == []
    assert board_for_player1.current_player.hidden_pair is not None
    assert len(board_for_player1.current_player.seven_cards) == 2
