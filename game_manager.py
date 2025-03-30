from card import CardPair
from card_pile import CardPile
from dice import roll_collection, DiceCollectionType, create_dice_collection, Dice
from enums import GameAction, GamePhase
from game_context import GameContext
from player import Player
from typing import List, Optional


class GameManager:
    def __init__(self, use_cli: bool = True):
        self.context = GameContext()
        self.game_running = False
        self.cli = None
        self.use_cli = use_cli
        if use_cli:
            try:
                from game_cli import GameCLI
                self.cli = GameCLI(self.context)
            except ImportError:
                print("Warning: GameCLI module not found. Running without CLI.")

    @property
    def card_pile(self) -> CardPile:
        return self.context.card_pile

    def start_game(self):
        """Start the game and handle the complete game flow."""
        if not self.context or len(self.context.players) != 2:
            raise ValueError("Game requires exactly 2 players")
        self.game_running = True
        # transition into GAME_INIT
        self.context.current_phase = GamePhase.GAME_INIT



    def process_action(self, action: GameAction) -> bool:
        """Process a player action"""
        if not self.context.is_valid_action(action):
            return False
            
        current_player = self.context.get_current_player()
        if not current_player:
            return False
            
        if action == GameAction.JOIN_GAME:
            if self.context.add_player(current_player):
                print(f"Player {len(self.context.players)} joined the game")
                return True
                
        elif action == GameAction.READY:
            if self.context.current_phase == GamePhase.LOBBY:
                if len(self.context.players) == 2:
                    self.context.current_phase = GamePhase.GAME_START
                    print("Both players ready - game starting")
                    return True
            elif self.context.current_phase == GamePhase.TURN_COMPLETE:
                # Only the second selector can roll dice
                if current_player == self.context.get_current_player():
                    self.context.roll_dice()
                    return True
                return False
                
        elif action == GameAction.START_GAME:
            if self.context.current_phase == GamePhase.GAME_START:
                self.context.current_phase = GamePhase.GAME_INIT
                print("Game starting...")
                return True
                
        elif action == GameAction.INITIALIZE_GAME:
            if self.context.current_phase == GamePhase.GAME_INIT:
                self.context.initialize_game()
                print("Game initialized")
                return True
                
        elif action == GameAction.SELECT_PAIR:
            if not self.cli:
                return False
            pair = self.cli.select_card_pair(
                self.context.get_available_pairs_for_p2() 
                if self.context.current_phase == GamePhase.TURN_SELECT_SECOND
                else self.context.available_pairs
            )
            if pair:
                return self.context.select_pair(pair)
                    
        elif action == GameAction.COLOR_CONVERT:
            if self.context.current_phase == GamePhase.FINAL_REVIEW:
                # Handle color conversion logic
                self.context.current_phase = GamePhase.GAME_END
                return True
                
        elif action == GameAction.CALCULATE_SCORES:
            if self.context.current_phase == GamePhase.GAME_END:
                # Calculate final scores
                return True
                
        elif action == GameAction.RETURN_TO_LOBBY:
            if self.context.current_phase == GamePhase.GAME_END:
                self.context = GameContext()  # Reset game state
                return True
                
        return False


    def draw_pairs(self) -> List[CardPair]:
        """Draw two pairs of cards for regular turns"""
        pairs = []
        for _ in range(3):
            pair = self.context.card_pile.draw_pair()
            if pair:
                pairs.append(pair)
        return pairs

    def add_player(self, player: Player) -> bool:
        """Add a player to the game"""
        if len(self.context.players) < 2:
            self.context.players.append(player)
            if len(self.context.players) == 2:
                self.context.current_phase = GamePhase.GAME_START
            return True
        return False

    def initialize_game(self) -> None:
        self.context.initialize_game()

    def roll_dice(self, dice_type: DiceCollectionType = DiceCollectionType.REGULAR, special_card_index: Optional[int] = None) -> None:
        """Roll dice for current player"""
        self.context.roll_dice(dice_type)

        if special_card_index is not None:
            special_card = self.context.dice_roller.seven_cards[special_card_index]
            self.context.dice_roller.use_seven_card(special_card)

    def start_turn(self) -> None:
        """Start a new turn"""
        self.context.start_turn()

    def select_pair(self, card_index: int) -> bool:
        """Select a card pair for the current turn"""
        if not self.context.available_pairs or card_index >= len(self.context.available_pairs):
            return False
        return self.context.select_pair(self.context.available_pairs[card_index])

    def end_review(self) -> None:
        """End the final review phase"""
        self.context.end_review()

    def calculate_final_results(self) -> dict:
        """Calculate final scores and determine the winner"""
        return self.context.calculate_final_results()

        