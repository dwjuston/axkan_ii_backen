import random
from typing import List, Optional, Dict

from pydantic import BaseModel

from card import CardPair, Card
from card_pile import CardPile
from enums import GamePhase, GameAction
from player import Player, PlayerView
from dice import roll_collection, DiceCollectionType, create_dice_collection, Dice
from board import Board

class GameResult(BaseModel):
    winner: int
    stock_price: int
    player_1: PlayerView
    player_2: PlayerView

    @staticmethod
    def create_sample():
        return {
            'winner': 1,
            'stock_price': 10,
            'player_1': {
                'uuid': '2',
                'name': 'Player 2',
                'player_id': 2,
                'selected_pairs': [],
                'seven_cards': [],
                'pnl': 0,
                'cost': 0,
                'value': 0
            },
            'player_2': {
                'uuid': '1',
                'name': 'Player 1',
                'player_id': 1,
                'selected_pairs': [],
                'seven_cards': [],
                'pnl': 0,
                'cost': 0,
                'value': 0
            }
        }



class GameContext:
    def __init__(self):
        self.current_phase: GamePhase = GamePhase.LOBBY
        self.players: List[Player] = []
        self.card_pile: Optional[CardPile] = None
        self.available_pairs: List[CardPair] = []
        self.selected_pair_index: Dict[str, int] = {}
        self.initial_price: Optional[int] = None
        self.current_price: Optional[int] = None
        self.current_turn: int = 1
        self.first_selector: Optional[Player] = None  # Track who selects first in current turn
        self.dice_result: list[int] = []
        self.dice_extra: int = 0

    def create_board(self, player_id: int) -> Board:
        current_player = self.player_1 if player_id == 0 else self.player_2
        opponent_player = self.player_2 if player_id == 0 else self.player_1

        board = Board(
            current_phase=self.current_phase,
            turn_number=self.current_turn,
            dice_result=self.dice_result,
            dice_extra=self.dice_extra,
            stock_price=self.current_price,
            first_selector=self.first_selector.player_id if self.first_selector else None,
            second_selector=self.second_selector.player_id if self.second_selector else None,
            dice_roller=self.dice_roller.player_id if self.dice_roller else None,
            available_pairs=self.available_pairs,
            selected_pair_index=self.selected_pair_index,
            current_player=current_player.get_player_view(self.current_price),
            opponent=opponent_player.get_opponent_view(self.current_price)
        )

        return board

    @property
    def second_selector(self) -> Optional[Player]:
        """Get the second selector for the current turn"""
        if self.first_selector == self.players[0]:
            return self.players[1]
        return self.players[0]

    @property
    def dice_roller(self) -> Optional[Player]:
        """Get the player responsible for rolling dice in the current turn"""
        return self.second_selector

    def get_current_player(self) -> Optional[Player]:
        """Get the current player based on game phase"""
        if not self.players or len(self.players) < 2:
            return None
            
        # Game phases
        if self.current_phase == GamePhase.GAME_INIT:
            return self.players[0]  # P1 is responsible for initial dice roll
        elif self.current_phase == GamePhase.TURN_SELECT_FIRST:
            return self.first_selector  # First selector (P1 in odd turns, P2 in even turns)
        elif self.current_phase == GamePhase.TURN_SELECT_SECOND:
            # Second selector is the other player
            return self.second_selector
        elif self.current_phase == GamePhase.TURN_COMPLETE:
            # Second selector is responsible for rolling dice
            return self.dice_roller
        return None

    def start_turn(self) -> None:
        """Handle automatic turn start actions"""
        if self.current_phase != GamePhase.TURN_START:
            raise ValueError("Invalid phase to start turn")

        # Determine first selector based on turn number
        mod = self.current_turn % 2
        # 1,3,5,7: P1 selects first
        self.first_selector = self.player_1 if mod == 1 else self.player_2

        # Draw new pairs
        self.selected_pair_index = {}
        self.available_pairs = self.draw_pairs()

        # Move to selection phase
        self.current_phase = GamePhase.TURN_SELECT_FIRST

    def start_review(self) -> None:
        if self.current_phase != GamePhase.FINAL_REVIEW:
            raise ValueError("Invalid phase to start review")

        # Move to review phase
        self.selected_pair_index = {}
        self.available_pairs = []


    def roll_dice(self, dice_collection_type: DiceCollectionType = DiceCollectionType.REGULAR) -> None:
        """Handle dice rolling and price update"""
        if self.current_phase == GamePhase.GAME_INIT:
            # Roll dice and set initial price
            # = roll_collection(DiceCollectionType.INITIAL)
            roll_result, dice_result, dice_extra = roll_collection(DiceCollectionType.INITIAL)
            self.set_initial_price(roll_result)
            self.dice_result = dice_result
            self.dice_extra = dice_extra
            self.current_phase = GamePhase.TURN_START
            return
            
        elif self.current_phase == GamePhase.TURN_COMPLETE:
            # Roll dice and update price
            roll_result, dice_result, dice_extra = roll_collection(dice_collection_type)
            self.dice_result = dice_result
            self.dice_extra = dice_extra
            self.update_price(roll_result)
            
        # Move to next turn
        if not self.is_last_turn():
            self.current_turn += 1
            self.current_phase = GamePhase.TURN_START  # Set phase to TURN_START
        else:
            self.current_phase = GamePhase.FINAL_REVIEW

    def draw_pairs(self) -> List[CardPair]:
        """Draw pairs for current turn"""
        pairs = []
        num_pairs = 3
        for _ in range(num_pairs):
            pair = self.card_pile.draw_pair()
            if pair:
                pairs.append(pair)
        return pairs

    def is_valid_action(self, action: GameAction) -> bool:
        """Check if an action is valid for the current phase"""
        if action == GameAction.JOIN_GAME:
            return self.current_phase == GamePhase.LOBBY and len(self.players) < 2
        elif action == GameAction.READY:
            if self.current_phase == GamePhase.LOBBY:
                return len(self.players) == 2
            elif self.current_phase == GamePhase.TURN_COMPLETE:
                return True
            return False
        elif action == GameAction.START_GAME:
            return self.current_phase == GamePhase.GAME_START
        elif action == GameAction.INITIALIZE_GAME:
            return self.current_phase == GamePhase.GAME_INIT
        elif action == GameAction.SELECT_PAIR:
            return self.current_phase in [GamePhase.TURN_SELECT_FIRST, GamePhase.TURN_SELECT_SECOND]
        elif action == GameAction.ROLL_DICE:
            return self.current_phase in [GamePhase.TURN_COMPLETE, GamePhase.GAME_INIT]
        elif action == GameAction.COLOR_CONVERT:
            return self.current_phase == GamePhase.FINAL_REVIEW
        elif action == GameAction.CALCULATE_SCORES:
            return self.current_phase == GamePhase.GAME_END
        elif action == GameAction.RETURN_TO_LOBBY:
            return self.current_phase == GamePhase.GAME_END
        return False

    @property
    def player_1(self) -> Optional[Player]:
        # check player_id == 0
        for player in self.players:
            if player.player_id == 0:
                return player
        return None

    @property
    def player_2(self) -> Optional[Player]:
        # check player_id == 1
        for player in self.players:
            if player.player_id == 1:
                return player
        return None

    def add_player(self, player: Player) -> bool:
        """Add a player to the game"""
        if len(self.players) < 2:
            self.players.append(player)
            if len(self.players) == 2:
                self.current_phase = GamePhase.GAME_START
            return True
        return False

    def initialize_game(self):
        """Initialize game components according to rules"""
        self.card_pile = CardPile()
        self.current_turn = 1
        self.current_phase = GamePhase.GAME_INIT
        self.current_price = None
        self.initial_price = None
        self.dice_result = []
        self.dice_extra = 0

        # flip a coin to determine who has player id 1 or 0
        rand = random.randint(0, 1)
        self.players[0].player_id = rand
        self.players[1].player_id = 1 - rand

        # reset portfolio
        for player in self.players:
            player.portfolio.reset()

        # Draw hidden pairs for each player
        for i in range(2):
            player = self.players[i]
            pair = self.card_pile.draw_pair()
            player.portfolio.add_hidden_pair(pair)
        
        # Give each player two 7s
        for i in range(2):
            player = self.players[i]
            seven_cards = self.card_pile.draw_seven_cards()
            player.portfolio.add_seven_card(seven_cards[0])
            player.portfolio.add_seven_card(seven_cards[1])


    def set_initial_price(self, roll_result: int) -> None:
        """Set initial price based on dice roll"""
        if roll_result >= 4:
            self.initial_price = 11
            self.current_price = 11
        else:
            self.initial_price = 10
            self.current_price = 10

    def update_price(self, roll_result: int) -> None:
        """Update the current price based on roll result"""
        self.current_price += roll_result
        # Wrap around logic
        if self.current_price <= 0:
            self.current_price += 20
        elif self.current_price > 20:
            self.current_price -= 20

    def is_last_turn(self) -> bool:
        """Check if this is the last turn"""
        return self.current_turn >= 7

    def select_pair(self, pair: CardPair) -> bool:
        """Handle pair selection and state transition"""
        current_player = self.get_current_player()
        if not current_player:
            return False
            
        if self.current_phase == GamePhase.TURN_SELECT_FIRST:
            print(f"{current_player.name} selected {pair}")
            current_player.select_pair(pair)
            self.selected_pair_index[current_player.uuid] = self.available_pairs.index(pair)
            self.current_phase = GamePhase.TURN_SELECT_SECOND
            return True
        elif self.current_phase == GamePhase.TURN_SELECT_SECOND:
            print(f"{current_player.name} selected {pair}")
            current_player.select_pair(pair)
            self.selected_pair_index[current_player.uuid] = self.available_pairs.index(pair)
            self.current_phase = GamePhase.TURN_COMPLETE
            return True
        return False

    def end_review(self) -> None:
        """Handle final review phase"""
        self.current_phase = GamePhase.GAME_END

    def calculate_final_results(self) -> GameResult:
        """
        Get final game results including:
        - Player scores
        - Winner
        - Stock Price
        - Selected Pairs
        - Hidden Pair
        """
        game_result = GameResult(
            winner=-1,
            stock_price=self.current_price,
            player_1=self.player_1.get_player_view(self.current_price),
            player_2=self.player_2.get_player_view(self.current_price)
        )

        # winner
        player1_score = game_result.player_1.pnl
        player2_score = game_result.player_2.pnl

        if player1_score > player2_score:
            game_result.winner = 0
        elif player1_score < player2_score:
            game_result.winner = 1
        else:
            game_result.winner = -1
        return game_result

    def convert_color(self, player_id: int, pair_index: int, special_card_index: int) -> bool:
        """Convert color of a pair for a player"""
        player = self.player_1 if player_id == 0 else self.player_2
        pair = player.portfolio.regular_pairs[pair_index] if pair_index >= 0 else player.hidden_pair
        return player.convert_card_color(pair, special_card_index)