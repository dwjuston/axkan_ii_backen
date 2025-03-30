import unittest
from unittest.mock import MagicMock, patch
from game_context import GameContext
from game_manager import GameManager
from player import Player
from card import Card, CardPair, CardSuit, CardRank, CardType
from enums import GamePhase, GameAction
from dice import roll_collection, create_dice_collection, DiceCollectionType

class TestTurnFlow(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.context = GameContext()
        self.manager = GameManager(use_cli=False)  # Disable CLI
        self.manager.context = self.context
        
        # Create test players
        self.p1 = Player(player_id="Player 1")
        self.p2 = Player(player_id="Player 2")
        
        # Add players to game
        self.context.add_player(self.p1)
        self.context.add_player(self.p2)
        
        # Create test card pairs
        self.pair1 = CardPair(
            small_card=Card(rank=CardRank.ACE, suit=CardSuit.HEARTS, card_type=CardType.SMALL),
            big_card=Card(rank=CardRank.KING, suit=CardSuit.SPADES, card_type=CardType.BIG)
        )
        self.pair2 = CardPair(
            small_card=Card(rank=CardRank.TWO, suit=CardSuit.DIAMONDS, card_type=CardType.SMALL),
            big_card=Card(rank=CardRank.QUEEN, suit=CardSuit.CLUBS, card_type=CardType.BIG)
        )
        self.pair3 = CardPair(
            small_card=Card(rank=CardRank.THREE, suit=CardSuit.HEARTS, card_type=CardType.SMALL),
            big_card=Card(rank=CardRank.JACK, suit=CardSuit.SPADES, card_type=CardType.BIG)
        )
        
        # Create seven cards
        self.seven_cards = [
            Card(rank=CardRank.SEVEN, suit=CardSuit.HEARTS, card_type=CardType.SPECIAL),
            Card(rank=CardRank.SEVEN, suit=CardSuit.SPADES, card_type=CardType.SPECIAL)
        ]
        
        # Mock dice roll
        self.roll_patcher = patch('game_context.roll_collection')
        self.mock_roll = self.roll_patcher.start()
        self.mock_roll.return_value = (MagicMock(), 5)  # (dice_collection, roll_result)

    def tearDown(self):
        """Clean up after each test"""
        self.roll_patcher.stop()

    def setup_card_pile_mock(self):
        """Set up a fresh card pile mock"""
        card_pile_mock = MagicMock()
        # Provide enough pairs for both turn 2 and turn 3
        card_pile_mock.draw_pair = MagicMock(side_effect=[self.pair1, self.pair2, self.pair3, self.pair1, self.pair2, self.pair3])
        card_pile_mock.draw_seven_cards = MagicMock(return_value=self.seven_cards)
        self.context.card_pile = card_pile_mock
        return card_pile_mock

    def test_turn_2_flow(self):
        """Test the complete flow of turn 2"""
        # Set up card pile mock
        card_pile_mock = self.setup_card_pile_mock()

        # Set up turn 2 directly
        self.context.current_turn = 2
        self.context.current_price = 11  # Set initial price
        
        # Test TURN_START
        self.context.start_turn()
        self.assertEqual(self.context.current_phase, GamePhase.TURN_SELECT_FIRST)
        self.assertEqual(self.context.first_selector, self.p2)  # P2 selects first in turn 2
        self.assertEqual(len(self.context.available_pairs), 3)  # Should have 2 pairs available in turn 2
        
        # Test TURN_SELECT_FIRST (P2's turn)
        self.assertEqual(self.context.get_current_player(), self.p2)
        self.assertTrue(self.context.is_valid_action(GameAction.SELECT_PAIR))
        self.assertEqual(len(self.p2.selected_pairs), 0)  # P2 has no pairs yet
        self.context.select_pair(self.context.available_pairs[0])  # Use the first available pair
        self.assertEqual(self.context.current_phase, GamePhase.TURN_SELECT_SECOND)
        self.assertEqual(len(self.context.selected_pairs), 1)
        self.assertEqual(len(self.context.available_pairs), 2)
        self.assertEqual(self.p2.selected_pairs[0], self.pair1)  # P2 selected pair1
        self.assertEqual(len(self.p1.selected_pairs), 0)  # P1 still has no pairs
        
        # Test TURN_SELECT_SECOND (P1's turn)
        self.assertEqual(self.context.get_current_player(), self.p1)
        self.assertTrue(self.context.is_valid_action(GameAction.SELECT_PAIR))
        self.context.select_pair(self.context.available_pairs[0])  # Use the remaining pair
        self.assertEqual(self.context.current_phase, GamePhase.TURN_COMPLETE)
        self.assertEqual(len(self.context.selected_pairs), 2)
        self.assertEqual(len(self.context.available_pairs), 1)
        self.assertEqual(self.p2.selected_pairs[0], self.pair1)  # P2 still has pair1
        self.assertEqual(self.p1.selected_pairs[0], self.pair2)  # P1 selected pair2
        
        # Test TURN_COMPLETE (P1 rolls dice)
        self.assertEqual(self.context.get_current_player(), self.p1)
        self.assertTrue(self.context.is_valid_action(GameAction.ROLL_DICE))
        
        # Test different dice types
        self.context.roll_dice(DiceCollectionType.INFLATION)  # This will use the mocked roll_collection
        
        # Check state after roll_dice but before start_turn
        self.assertEqual(self.context.current_turn, 3)
        self.assertEqual(self.context.current_phase, GamePhase.TURN_START)


        # Now start the turn
        self.context.start_turn()
        self.assertEqual(self.context.current_phase, GamePhase.TURN_SELECT_FIRST)

    def test_invalid_actions(self):
        """Test invalid actions in turn 2"""
        # Set up card pile mock
        card_pile_mock = self.setup_card_pile_mock()
        
        # Set up turn 2 directly
        self.context.current_turn = 2
        
        # Test invalid actions in TURN_SELECT_FIRST
        self.context.start_turn()
        self.assertFalse(self.context.is_valid_action(GameAction.ROLL_DICE))
        self.assertFalse(self.context.is_valid_action(GameAction.COLOR_CONVERT))
        
        # Test invalid actions in TURN_SELECT_SECOND
        self.context.select_pair(self.context.available_pairs[0])  # Use the first available pair
        self.assertFalse(self.context.is_valid_action(GameAction.ROLL_DICE))
        self.assertFalse(self.context.is_valid_action(GameAction.COLOR_CONVERT))
        
        # Test invalid actions in TURN_COMPLETE
        self.context.select_pair(self.context.available_pairs[0])  # Use the remaining pair
        self.assertFalse(self.context.is_valid_action(GameAction.SELECT_PAIR))
        self.assertFalse(self.context.is_valid_action(GameAction.COLOR_CONVERT))

    def test_player_order(self):
        """Test player order in turn 2"""
        # Set up card pile mock
        card_pile_mock = self.setup_card_pile_mock()
        
        # Set up turn 2 directly
        self.context.current_turn = 2
        
        # Test first selector (P2)
        self.context.start_turn()
        self.assertEqual(self.context.first_selector, self.p2)
        self.assertEqual(self.context.get_current_player(), self.p2)
        
        # Test second selector (P1)
        self.context.select_pair(self.context.available_pairs[0])  # Use the first available pair
        self.assertEqual(self.context.get_current_player(), self.p1)
        
        # Test dice roller (P1)
        self.context.select_pair(self.context.available_pairs[0])  # Use the remaining pair
        self.assertEqual(self.context.get_current_player(), self.p1)

    def test_turn_5_flow(self):
        """Test the complete flow of turn 5"""
        # Set up card pile mock
        card_pile_mock = self.setup_card_pile_mock()
        
        # Set up turn 5 directly
        self.context.current_turn = 5
        self.context.current_price = 11  # Set initial price
        
        # Test TURN_START
        self.context.start_turn()
        self.assertEqual(self.context.current_phase, GamePhase.TURN_SELECT_FIRST)
        self.assertEqual(self.context.first_selector, self.p1)  # P1 selects first in turn 5
        self.assertEqual(len(self.context.available_pairs), 3)  # Should have 3 pairs available
        
        # Test TURN_SELECT_FIRST (P1's turn)
        self.assertEqual(self.context.get_current_player(), self.p1)
        self.assertTrue(self.context.is_valid_action(GameAction.SELECT_PAIR))
        self.assertEqual(len(self.p1.selected_pairs), 0)  # P1 has no pairs yet
        self.context.select_pair(self.context.available_pairs[0])  # Use the first available pair
        self.assertEqual(self.context.current_phase, GamePhase.TURN_SELECT_SECOND)
        self.assertEqual(len(self.context.selected_pairs), 1)
        self.assertEqual(len(self.context.available_pairs), 2)
        self.assertEqual(self.p1.selected_pairs[0], self.pair1)  # P1 selected pair1
        self.assertEqual(len(self.p2.selected_pairs), 0)  # P2 still has no pairs
        
        # Test TURN_SELECT_SECOND (P2's turn)
        self.assertEqual(self.context.get_current_player(), self.p2)
        self.assertTrue(self.context.is_valid_action(GameAction.SELECT_PAIR))
        self.context.select_pair(self.context.available_pairs[0])  # Use the remaining pair
        self.assertEqual(self.context.current_phase, GamePhase.TURN_COMPLETE)
        self.assertEqual(len(self.context.selected_pairs), 2)
        self.assertEqual(len(self.context.available_pairs), 1)
        self.assertEqual(self.p1.selected_pairs[0], self.pair1)  # P1 still has pair1
        self.assertEqual(self.p2.selected_pairs[0], self.pair2)  # P2 selected pair2
        
        # Test TURN_COMPLETE (P2 rolls dice)
        self.assertEqual(self.context.get_current_player(), self.p2)
        self.assertTrue(self.context.is_valid_action(GameAction.ROLL_DICE))
        
        # Test different dice types
        self.context.roll_dice()
        
        # Check state after roll_dice but before start_turn
        self.assertEqual(self.context.current_turn, 6)
        self.assertEqual(self.context.current_phase, GamePhase.TURN_START)
        
        # Now start the turn
        self.context.start_turn()
        self.assertEqual(self.context.current_phase, GamePhase.TURN_SELECT_FIRST)

    def test_game_init_flow(self):
        """Test the complete flow of GAME_INIT phase"""
        # Set up card pile mock
        card_pile_mock = self.setup_card_pile_mock()
        
        # Set up GAME_INIT phase
        self.context.current_phase = GamePhase.GAME_INIT
        
        # Initialize game (deals cards)
        self.context.initialize_game()
        
        # Test seven cards distribution from player
        self.assertEqual(len(self.context.players[0].portfolio.seven_cards), 2)  # P1 should have 2 seven cards
        self.assertEqual(len(self.context.players[1].portfolio.seven_cards), 2)  # P2 should have 2 seven cards
        self.assertEqual(self.context.players[0].portfolio.seven_cards[0].rank, CardRank.SEVEN)
        self.assertEqual(self.context.players[1].portfolio.seven_cards[0].rank, CardRank.SEVEN)


        # Test hidden pairs distribution
        self.assertIsNotNone(self.context.players[0].portfolio.hidden_pair)  # P1 should have 1 hidden pair
        self.assertIsNotNone(self.context.players[1].portfolio.hidden_pair)
        
        # Test initial dice roll (P1's turn)
        self.assertEqual(self.context.get_current_player(), self.p1)
        self.assertTrue(self.context.is_valid_action(GameAction.ROLL_DICE))

        # Roll Dice
        self.context.roll_dice()

        # Check the initial price is either 10 or 11
        self.assertIn(self.context.initial_price, [10, 11])
            
        # Verify transition to TURN_START
        self.assertEqual(self.context.current_phase, GamePhase.TURN_START)
        self.assertEqual(self.context.current_turn, 1)

    def test_turn_1_flow(self):
        """Test the complete flow of turn 1"""
        # Set up card pile mock
        card_pile_mock = self.setup_card_pile_mock()
        
        # Set up turn 1 directly
        self.context.current_turn = 1
        self.context.current_phase = GamePhase.TURN_START
        self.context.current_price = 10
        self.context.initial_price = 10
        
        # Test TURN_START
        self.context.start_turn()
        self.assertEqual(self.context.current_phase, GamePhase.TURN_SELECT_FIRST)
        self.assertEqual(self.context.first_selector, self.p1)  # P1 selects first in turn 1
        self.assertEqual(len(self.context.available_pairs), 3)  # Should have 3 pairs available
        
        # Test TURN_SELECT_FIRST (P1's turn)
        self.assertEqual(self.context.get_current_player(), self.p1)
        self.assertTrue(self.context.is_valid_action(GameAction.SELECT_PAIR))
        self.context.select_pair(self.context.available_pairs[0])  # Use the first available pair
        self.assertEqual(self.context.current_phase, GamePhase.TURN_SELECT_SECOND)
        
        # Test TURN_SELECT_SECOND (P2's turn)
        self.assertEqual(self.context.get_current_player(), self.p2)
        self.assertTrue(self.context.is_valid_action(GameAction.SELECT_PAIR))
        self.context.select_pair(self.context.available_pairs[0])  # Use the remaining pair
        self.assertEqual(self.context.current_phase, GamePhase.TURN_COMPLETE)
        
        # Test TURN_COMPLETE (P2 rolls dice)
        self.assertEqual(self.context.get_current_player(), self.p2)
        self.assertTrue(self.context.is_valid_action(GameAction.ROLL_DICE))

        self.context.roll_dice()
        self.assertEqual(self.context.current_phase, GamePhase.TURN_START)
        self.assertEqual(self.context.current_turn, 2)

            


    def test_turn_8_flow(self):
        """Test the complete flow of turn 8 (final turn)"""
        # Set up card pile mock
        card_pile_mock = self.setup_card_pile_mock()
        
        # Set up turn 8 directly
        self.context.current_turn = 8
        self.context.current_price = 11  # Set current price
        
        # Test TURN_START
        self.context.start_turn()
        self.assertEqual(self.context.current_phase, GamePhase.FINAL_REVIEW)

if __name__ == '__main__':
    unittest.main() 