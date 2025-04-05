from dice import DiceCollectionType
from enums import GameAction
from game_manager import GameManager


def test_game_manager() -> None:
    game_manager = GameManager()
    uuid_1 = "1"
    uuid_2 = "2"
    game_manager.take_action(uuid_1, GameAction.JOIN_GAME, player_name = "AAA")
    game_manager.take_action(uuid_2, GameAction.JOIN_GAME, player_name = "BBB")
    game_manager.take_action(uuid_1, GameAction.READY)
    game_manager.take_action(uuid_2, GameAction.READY)

    uuid_1 = game_manager.context.player_1.uuid
    uuid_2 = game_manager.context.player_2.uuid
    game_manager.take_action(uuid_1, GameAction.ROLL_DICE)
    # Turn 1
    game_manager.take_action(uuid_1, GameAction.SELECT_PAIR, pair_index = 0)
    game_manager.take_action(uuid_2, GameAction.SELECT_PAIR, pair_index = 1)
    game_manager.take_action(uuid_2, GameAction.ROLL_DICE)
    # Turn 2
    game_manager.take_action(uuid_2, GameAction.SELECT_PAIR, pair_index = 0)
    game_manager.take_action(uuid_1, GameAction.SELECT_PAIR, pair_index = 1)
    game_manager.take_action(uuid_1, GameAction.ROLL_DICE)
    # Turn 3
    game_manager.take_action(uuid_1, GameAction.SELECT_PAIR, pair_index = 0)
    game_manager.take_action(uuid_2, GameAction.SELECT_PAIR, pair_index = 1)
    game_manager.take_action(uuid_2, GameAction.ROLL_DICE)
    # Turn 4
    game_manager.take_action(uuid_2, GameAction.SELECT_PAIR, pair_index = 0)
    game_manager.take_action(uuid_1, GameAction.SELECT_PAIR, pair_index = 1)
    game_manager.take_action(uuid_1, GameAction.ROLL_DICE)
    # Turn 5
    game_manager.take_action(uuid_1, GameAction.SELECT_PAIR, pair_index = 0)
    game_manager.take_action(uuid_2, GameAction.SELECT_PAIR, pair_index = 1)
    game_manager.take_action(uuid_2, GameAction.ROLL_DICE)
    # Turn 6
    game_manager.take_action(uuid_2, GameAction.SELECT_PAIR, pair_index = 0)
    game_manager.take_action(uuid_1, GameAction.SELECT_PAIR, pair_index = 1)
    game_manager.take_action(uuid_1, GameAction.ROLL_DICE, dice_collection_type = DiceCollectionType.SUPPLY_SHOCK)
    # Turn 7
    game_manager.take_action(uuid_1, GameAction.SELECT_PAIR, pair_index = 0)
    game_manager.take_action(uuid_2, GameAction.SELECT_PAIR, pair_index = 1)
    game_manager.take_action(uuid_2, GameAction.ROLL_DICE, dice_collection_type = DiceCollectionType.INFLATION)

    # Final Review
    game_manager.take_action(uuid_1, GameAction.COLOR_CONVERT, pair_index=-1, special_card_index=0)
    game_manager.take_action(uuid_1, GameAction.COLOR_CONVERT, pair_index=0, special_card_index=0)
    game_manager.take_action(uuid_2, GameAction.END_REVIEW)
    game_manager.take_action(uuid_1, GameAction.END_REVIEW)

    # Restart
    game_manager.take_action(uuid_1, GameAction.READY)
    game_manager.take_action(uuid_2, GameAction.READY)
    uuid_1 = game_manager.context.player_1.uuid
    uuid_2 = game_manager.context.player_2.uuid
    game_manager.take_action(uuid_1, GameAction.ROLL_DICE)
    # Turn 1
    game_manager.take_action(uuid_1, GameAction.SELECT_PAIR, pair_index = 0)
    game_manager.take_action(uuid_2, GameAction.SELECT_PAIR, pair_index = 1)
    game_manager.take_action(uuid_2, GameAction.ROLL_DICE)

