from dataclasses import dataclass

from api.models import PlayerMetadata
from card import CardPair
from card_pile import CardPile
from dice import roll_collection, DiceCollectionType, create_dice_collection, Dice
from enums import GameAction, GamePhase
from game_context import GameContext
from player import Player
from typing import List, Optional
from api.websocket import WebSocketMessage, websocket_manager

class GameManager:
    def __init__(self, game_id: str):
        self.game_id = game_id
        self.context = GameContext()
        self.ready_player_count = 0
        self.game_running = False

    async def take_action(self,
                    player_uuid: str,
                    action: GameAction,
                    player_name: Optional[str] = None,
                    pair_index: Optional[int] = None,
                    special_card_index: Optional[int] = None,
                    dice_collection_type: Optional[str] = None
                    ) -> None:
        # if-else for each phase
        current_phase = self.context.current_phase
        if current_phase == GamePhase.LOBBY:
            if action == GameAction.JOIN_GAME:
                if len(self.context.players) < 2:
                    if player_name:
                        player = Player(uuid=player_uuid, player_id=len(self.context.players), name=player_name)
                        # when the second player joined, the game phase is automatically set to GAME_START

                        player_metadata = PlayerMetadata(
                            game_id=self.game_id,
                            player_uuid=player.uuid,
                            player_name=player.name,
                            opponent_uuid=self.context.players[0].uuid if len(self.context.players) > 0 else None,
                            opponent_name=self.context.players[0].name if len(self.context.players) > 0 else None
                        )
                        self.context.add_player(player)
                        await self.notify_all("join", player_metadata.model_dump_json())
                    else:
                        raise ValueError("Player name and uuid required to create a player")
                else:
                    raise ValueError("Game already has two players")

        elif current_phase == GamePhase.GAME_START:
            if action == GameAction.READY:
                if self.ready_player_count == 0:
                    self.ready_player_count += 1
                    await self.notify_all("ready", player_uuid)
                elif self.ready_player_count == 1:
                    self.ready_player_count = 0
                    await self.notify_all("ready", player_uuid)
                    self.context.initialize_game()

                    player1 = self.context.player_1
                    player2 = self.context.player_2
                    await self.notify_all("init", f"{player1.uuid},{player2.uuid}")


        elif current_phase == GamePhase.GAME_INIT:
            if action == GameAction.ROLL_DICE:
                self.context.roll_dice()
                self.context.start_turn()
                player1 = self.context.player_1
                player2 = self.context.player_2
                await self.notify(player1.uuid, "board", self.context.create_board(player1.player_id).model_dump_json())
                await self.notify(player2.uuid, "board", self.context.create_board(player2.player_id).model_dump_json())

        elif current_phase == GamePhase.TURN_SELECT_FIRST:
            if action == GameAction.SELECT_PAIR:
                if pair_index is None:
                    raise ValueError("Card index required to select a pair")
                if player_uuid != self.context.first_selector.uuid:
                    raise ValueError("Only the first selector can choose a pair now")
                pair = self.context.available_pairs[pair_index]
                self.context.select_pair(pair)
                player1 = self.context.player_1
                player2 = self.context.player_2
                await self.notify(player1.uuid, "board", self.context.create_board(player1.player_id).model_dump_json())
                await self.notify(player2.uuid, "board", self.context.create_board(player2.player_id).model_dump_json())

        elif current_phase == GamePhase.TURN_SELECT_SECOND:
            if action == GameAction.SELECT_PAIR:
                if pair_index is None:
                    raise ValueError("Card index required to select a pair")
                if player_uuid != self.context.second_selector.uuid:
                    raise ValueError("Only the second selector can choose a pair now")
                pair = self.context.available_pairs[pair_index]
                self.context.select_pair(pair)
                player1 = self.context.player_1
                player2 = self.context.player_2
                await self.notify(player1.uuid, "board", self.context.create_board(player1.player_id).model_dump_json())
                await self.notify(player2.uuid, "board", self.context.create_board(player2.player_id).model_dump_json())


        elif current_phase == GamePhase.TURN_COMPLETE:
            if action == GameAction.ROLL_DICE:
                if player_uuid != self.context.dice_roller.uuid:
                    raise ValueError("Only the dice roller can roll the dice")

                if special_card_index is not None and dice_collection_type is not None:
                    self.context.roll_dice(DiceCollectionType(dice_collection_type))
                    player = self.context.player_1 if player_uuid == self.context.player_1.uuid else self.context.player_2
                    seven_card = player.seven_cards[special_card_index]
                    player.remove_seven_card(seven_card)
                else:
                    self.context.roll_dice()

                if self.context.current_phase == GamePhase.TURN_START:
                    self.context.start_turn()
                    player1 = self.context.player_1
                    player2 = self.context.player_2
                    await self.notify(player1.uuid, "board",
                                self.context.create_board(player1.player_id).model_dump_json())
                    await self.notify(player2.uuid, "board",
                                self.context.create_board(player2.player_id).model_dump_json())
                elif self.context.current_phase == GamePhase.FINAL_REVIEW:
                    self.context.start_review()
                    player1 = self.context.player_1
                    player2 = self.context.player_2
                    await self.notify(player1.uuid, "board",
                                self.context.create_board(player1.player_id).model_dump_json())
                    await self.notify(player2.uuid, "board",
                                self.context.create_board(player2.player_id).model_dump_json())

        elif current_phase == GamePhase.FINAL_REVIEW:
            if action == GameAction.COLOR_CONVERT:
                if special_card_index is None:
                    raise ValueError("Special card index required to convert color")
                if pair_index is None:
                    raise ValueError("Pair index required to convert color")
                player = self.context.player_1 if player_uuid == self.context.player_1.uuid else self.context.player_2
                self.context.convert_color(player.player_id, pair_index, special_card_index)
                await self.notify(player_uuid, "board", self.context.create_board(player.player_id).model_dump_json())

            elif action == GameAction.END_REVIEW:
                if self.ready_player_count == 0:
                    self.ready_player_count += 1
                    await self.notify_all("end", player_uuid)
                elif self.ready_player_count == 1:
                    self.ready_player_count = 0
                    self.context.end_review()

                    # send over the final result
                    await self.notify_all("result", self.context.calculate_final_results().model_dump_json())

        elif current_phase == GamePhase.GAME_END:
            if action == GameAction.READY:
                if self.ready_player_count == 0:
                    self.ready_player_count += 1
                    await self.notify_all("ready", player_uuid)
                elif self.ready_player_count == 1:
                    self.ready_player_count = 0
                    self.context.initialize_game()
                    await self.notify_all("ready", player_uuid)

        else:
            await self.notify_all("error", player_uuid)

    async def notify(self, player_uuid: str, message_type: str, message: str) -> None:
        await websocket_manager.send(self.game_id, [player_uuid], message_type, message)

    async def notify_all(self, message_type: str, message: str) -> None:
        await websocket_manager.send(self.game_id, None, message_type, message)

    def get_player_uuid(self, player_id: int) -> str:
        for player in self.context.players:
            if player.player_id == player_id:
                return player.uuid
        raise ValueError("Player not found")

        