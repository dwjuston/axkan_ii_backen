from typing import List, Optional, Dict
from card import CardPair, Card
from card_pile import CardPile
from enums import GamePhase, GameAction
from player import Player
from dice import roll_collection, DiceCollectionType, create_dice_collection, Dice
from board import Board

class GameContext:
    def __init__(self):
        self.current_phase: GamePhase = GamePhase.LOBBY
        self.players: List[Player] = []
        self.card_pile: Optional[CardPile] = None
        self.available_pairs: List[CardPair] = []
        self.selected_pairs: List[CardPair] = []
        self.initial_price: Optional[int] = None
        self.current_price: Optional[int] = None
        self.current_turn: int = 1
        self.first_selector: Optional[Player] = None  # Track who selects first in current turn

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
        if not self.players:
            return None
            
        # Lobby phase
        if self.current_phase == GamePhase.LOBBY:
            if len(self.players) == 1:
                return self.players[0]  # Player 1 is waiting for Player 2
            return None
            
        # Game phases
        if self.current_phase == GamePhase.GAME_INIT:
            return self.players[0]  # P1 is responsible for initial dice roll
        elif self.current_phase == GamePhase.TURN_SELECT_FIRST:
            return self.first_selector  # First selector (P1 in odd turns, P2 in even turns)
        elif self.current_phase == GamePhase.TURN_SELECT_SECOND:
            # Second selector is the other player
            return self.players[1] if self.first_selector == self.players[0] else self.players[0]
        elif self.current_phase == GamePhase.TURN_COMPLETE:
            # Second selector is responsible for rolling dice
            return self.players[1] if self.first_selector == self.players[0] else self.players[0]
        return None

    def start_turn(self) -> None:
        """Handle automatic turn start actions"""
        # if last turn, skip to TURN_COMPLETE
        if self.is_last_turn():
            self.current_phase = GamePhase.FINAL_REVIEW
            return


        # Determine first selector based on turn number
        self.first_selector = self.players[0] if self.current_turn % 2 == 1 else self.players[1]
        
        # Draw new pairs
        self.selected_pairs = []
        self.available_pairs = self.draw_pairs()
        
        # Recalculate scores for all players
        for player in self.players:
            player.recalculate_score(self.current_price)
            
        # Move to selection phase
        self.current_phase = GamePhase.TURN_SELECT_FIRST

    def roll_dice(self, dice_collection_type: DiceCollectionType = DiceCollectionType.REGULAR) -> None:
        """Handle dice rolling and price update"""
        if self.current_phase == GamePhase.GAME_INIT:
            # Roll dice and set initial price
            _, roll_result = roll_collection(DiceCollectionType.INITIAL)
            self.set_initial_price(roll_result)
            self.current_phase = GamePhase.TURN_START
            return
            
        elif self.current_phase == GamePhase.TURN_COMPLETE:
            # Roll dice and update price
            _, roll_result = roll_collection(dice_collection_type)

            self.update_price(roll_result)

            # Reset Turn State for both players
            for player in self.players:
                player.reset_turn_state()
            
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

    def get_available_pairs_for_p2(self) -> List[CardPair]:
        """Get available pairs for Player 2 after Player 1's selection"""
        if not self.selected_pairs:
            return self.available_pairs
        return [pair for pair in self.available_pairs if pair != self.selected_pairs[-1]]

    def is_last_turn(self) -> bool:
        """Check if this is the last turn"""
        return self.current_turn >= 8

    def select_pair(self, pair: CardPair) -> bool:
        """Handle pair selection and state transition"""
        current_player = self.get_current_player()
        if not current_player:
            return False
            
        if self.current_phase == GamePhase.TURN_SELECT_FIRST:
            if current_player.select_pair(pair):
                self.selected_pairs.append(pair)
                self.available_pairs.remove(pair)
                self.current_phase = GamePhase.TURN_SELECT_SECOND
                return True
        elif self.current_phase == GamePhase.TURN_SELECT_SECOND:
            if current_player.select_pair(pair):
                self.selected_pairs.append(pair)
                self.available_pairs.remove(pair)
                self.current_phase = GamePhase.TURN_COMPLETE
                return True
        return False

    def complete_turn(self) -> None:
        """Handle turn completion and transition to next turn"""
        self.current_turn += 1
        if self.is_last_turn():
            self.current_phase = GamePhase.FINAL_REVIEW
        else:
            self.start_turn()  # Automatically start next turn

    def end_review(self) -> None:
        """Handle final review phase"""
        self.current_phase = GamePhase.GAME_END

    def create_board_for_player(self, player_id: str) -> Board:
        """
        Creates a Board instance with player-specific view.
        
        Args:
            player_id: ID of the player requesting the board
            
        Returns:
            Board: Board instance with appropriate data visibility
            
        The board shows:
        - For current player: all their data including hidden pairs
        - For opponent: visible data only (no hidden pairs)
        - Common game state: available pairs, selected pairs, roles
        """
        # Find current player and opponent
        current_player = next((p for p in self.players if p.player_id == player_id), None)
        if not current_player:
            raise ValueError(f"Player {player_id} not found in game")
            
        opponent = next((p for p in self.players if p.player_id != player_id), None)
        if not opponent:
            raise ValueError("No opponent found")
            
        # Create filtered opponent view (without hidden pairs)
        opponent_view = Player(
            player_id=opponent.player_id,
            portfolio=opponent.portfolio.get_filtered_portfolio(),
            has_selected=opponent.has_selected,
            current_score=opponent.current_score
        )
        
        return Board(
            dice_result=0,  # Current stock price
            stock_price=self.current_price,  # Will be None initially
            turn_number=self.current_turn,
            available_pairs=self.available_pairs,
            first_selector=self.first_selector.player_id if self.first_selector else "",
            second_selector=self.second_selector.player_id if self.second_selector else "",
            dice_roller=self.dice_roller.player_id if self.dice_roller else "",
            current_player=current_player,
            opponent=opponent_view,
            current_phase=self.current_phase,
            selected_pairs=self.selected_pairs
        )

    def calculate_final_results(self) -> Dict[str, int]:
        """
        Get final game results including:
        - Player scores
        - Winner
        - Stock Price
        - Selected Pairs
        - Hidden Pair
        """
        results = {}
        # stock price
        results["stock_price"] = self.current_price
        # player 1 data: selected pairs, hidden pair, current score, cost, pnl
        for player in self.players:
            player.recalculate_score(self.current_price)
            results[player.player_id] = {
                "selected_pairs": [pair.dict() for pair in player.selected_pairs],
                "hidden_pair": player.hidden_pairs[0].dict(),
                "current_score": player.portfolio.get_total_value(self.current_price),
                "cost": player.portfolio.total_cost,
                "pnl": player.portfolio.get_pnl(self.current_price)
            }
        # winner
        if self.players[0].current_score > self.players[1].current_score:
            results["winner"] = self.players[0].player_id
        elif self.players[0].current_score < self.players[1].current_score:
            results["winner"] = self.players[1].player_id
        else:
            results["winner"] = "Tie"
        return results