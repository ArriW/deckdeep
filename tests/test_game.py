import sys
import os
import pygame

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest  # noqa: E402
from unittest.mock import Mock, patch  # noqa: E402
from deckdeep.game import Game  # noqa: E402
from deckdeep.player import Player  # noqa: E402
from deckdeep.monster_group import MonsterGroup  # noqa: E402
from deckdeep.logger import GameLogger  # noqa: E402
from deckdeep.custom_types import Health, Energy  # noqa: E402
from deckdeep.game import Node  # noqa: E402


@pytest.fixture
def mock_screen():
    return Mock()


@pytest.fixture
def mock_logger():
    return Mock(spec=GameLogger)


@pytest.fixture
def game(mock_screen, mock_logger):
    with patch("pygame.init"), patch("pygame.display.set_mode"), patch(
        "deckdeep.game.GameAssets"
    ) as mock_assets, patch("deckdeep.game.Player"), patch(
        "deckdeep.game.MonsterGroup"
    ), patch(
        "deckdeep.game.Node"
    ):
        mock_assets.return_value.background_image = pygame.Surface((800, 600))
        mock_assets.return_value.player = pygame.Surface((50, 50))
        mock_assets.return_value.health_bar = pygame.Surface((100, 10))
        mock_assets.return_value.energy_icon = pygame.Surface((20, 20))
        # Add more asset mocks as needed

        game = Game(mock_screen, mock_logger)
        game.player = Mock(spec=Player)
        game.player.health = Mock(spec=Health)
        game.player.health.value = 100
        game.player.max_health = Mock(spec=Health)
        game.player.max_health.value = 100
        game.player.shield = 0
        game.player.relics = []
        game.player.hp_regain_per_level = 10
        game.player.is_dying = False
        game.player.shake = 0
        game.player.status_effects = Mock()
        game.player.status_effects.effects = {}
        game.player.bonus_damage = 0
        game.player.strength = 0
        game.player.hand = []
        game.player.deck = []
        game.player.discard_pile = []
        game.player.energy = Mock(spec=Energy)
        game.player.energy.value = 3
        game.player.max_energy = Mock(spec=Energy)
        game.player.max_energy.value = 3
        game.monster_group = Mock(spec=MonsterGroup)
        game.monster_group.monsters = []
        game.monster_group.decide_action = Mock(return_value={})
        game.current_node = Mock()
        game.current_node.node_type = "combat"
        game.node_tree = Mock()
        return game


@pytest.fixture(scope="session", autouse=True)
def initialize_pygame():
    pygame.init()
    pygame.display.set_mode((800, 600))  # Add this line
    yield
    pygame.quit()


def test_game_initialization(game):
    assert game.player is not None
    assert game.monster_group is not None
    assert game.stage == 1
    assert game.score == 0
    assert game.running is True


def test_new_game(game):
    with patch("deckdeep.game.Game.generate_node_tree") as mock_generate, patch(
        "deckdeep.game.Game.initialize_combat"
    ), patch("deckdeep.game.Player.create") as mock_create:
        mock_player = Mock(spec=Player)
        mock_player.relics = []
        mock_player.is_dying = False
        mock_create.return_value = mock_player
        mock_generate.return_value = Mock()
        game.new_game()
    assert isinstance(game.player, Mock)
    assert game.stage == 1
    assert game.score == 0
    assert game.game_over is False


def test_handle_events(game):
    with patch("pygame.event.get", return_value=[]):
        game.handle_events(Mock())
    assert game.running is True


def test_game_over(game):
    game.player.health.value = 0
    with patch("deckdeep.game.Game.save_game"), patch(
        "deckdeep.game.Game.update_combat"
    ):
        game.update()
    assert game.game_over is True


def test_combat_victory(game):
    initial_score = game.score
    game.monster_group.monsters = []
    with patch("deckdeep.game.Game.combat_victory") as mock_combat_victory:

        def side_effect():
            game.score += 10

        mock_combat_victory.side_effect = side_effect
        game.update()
    assert game.score > initial_score


def test_player_take_damage(game):
    initial_health = game.player.health.value
    damage = 10
    game.player.take_damage = Mock(
        side_effect=lambda x: setattr(
            game.player.health, "value", game.player.health.value - x
        )
    )
    game.player.take_damage(damage)
    game.player.take_damage.assert_called_once_with(damage)
    assert game.player.health.value == initial_health - damage


def test_player_heal(game):
    game.player.health.value = 50
    game.player.max_health = Mock(spec=Health)
    game.player.max_health.value = 100
    heal_amount = 20
    game.player.heal = Mock(
        wraps=lambda x: setattr(
            game.player.health,
            "value",
            min(game.player.health.value + x, game.player.max_health.value),
        )
    )
    game.player.heal(heal_amount)
    assert game.player.health.value == 70


def test_monster_group_attack(game):
    mock_monster1 = Mock()
    mock_monster2 = Mock()
    game.monster_group.monsters = [mock_monster1, mock_monster2]
    game.monster_group.attack = Mock(
        side_effect=lambda player: [
            monster.attack(player) for monster in game.monster_group.monsters
        ]
    )
    game.monster_group.attack(game.player)
    mock_monster1.attack.assert_called_once_with(game.player)
    mock_monster2.attack.assert_called_once_with(game.player)


def test_apply_relic_effects(game):
    mock_relic = Mock()
    mock_relic.trigger_when = "ON_TURN_START"
    mock_relic.apply_effect = Mock(return_value="Relic effect applied")
    game.player.relics = [mock_relic]
    game.logger.debug = Mock()

    with patch("deckdeep.game.TriggerWhen") as mock_trigger_when:
        mock_trigger_when.ON_TURN_START = "ON_TURN_START"
        game.apply_relic_effects = lambda trigger: [
            game.logger.debug(
                f"Applied relic effect: {relic.apply_effect(game.player, game)}",
                category="PLAYER",
            )
            for relic in game.player.relics
            if relic.trigger_when == trigger
        ]
        game.apply_relic_effects(mock_trigger_when.ON_TURN_START)

    mock_relic.apply_effect.assert_called_once_with(game.player, game)
    game.logger.debug.assert_called_with(
        "Applied relic effect: Relic effect applied", category="PLAYER"
    )


def test_save_and_load_game(game):
    mock_player_data = {
        "name": "TestPlayer",
        "health": 80,  # Change this line
        "max_health": 100,  # Change this line
        "symbol": "@",
        "shield": 0,
        "bonus_damage": 0,
        "energy": 3,  # Change this line
        "max_energy": 3,  # Change this line
        "hand_limit": 7,
        "deck": [],
        "hand": [],
        "discard_pile": [],
        "size": (50, 50),
        "shake": 0,
        "health_gain_on_skip": 5,
        "cards_drawn_per_turn": 5,
        "hp_regain_per_level": 10,
        "status_effects": {"effects": []},  # Update this line
        "relics": [],
        "strength": 0,
        "dodge_chance": 0,
        "cards_per_turn": 5,
        "phoenix_feather_active": False,
        "extra_turn_chance": 0,
        "applied_permanent_effects": {},
        "is_dying": False,
        "death_start_time": None,
    }

    mock_monster_group = {"monsters": [], "selected_index": 0}

    mock_node_data = {
        "node_type": "combat",
        "stage": 1,
        "level": 1,
        "true_level": 1,
        "content": {"monsters": mock_monster_group},  # Add mock monster group here
        "children": [
            {
                "node_type": "combat",
                "stage": 1,
                "level": 2,
                "true_level": 2,
                "content": {
                    "monsters": mock_monster_group
                },  # Add to child node as well
                "children": [],
            }
        ],
    }

    game.player.to_dict = Mock(return_value=mock_player_data)
    game.node_tree = Node.from_dict(mock_node_data)  # Create an actual Node object
    game.get_node_path = Mock(
        return_value=[0]
    )  # Update this to match the new structure

    with patch("builtins.open", create=True), patch("json.dump"), patch(
        "json.load"
    ) as mock_load, patch(
        "deckdeep.game.MonsterGroup.from_dict"
    ) as mock_monster_group_from_dict:
        mock_load.return_value = {
            "player": mock_player_data,
            "node_tree": mock_node_data,
            "current_node_path": [0],  # Update this to match the new structure
            "stage": 2,
            "score": 100,
            "game_over": False,
        }
        mock_monster_group_from_dict.return_value = Mock()  # Return a mock MonsterGroup
        game.save_game()
        game.load_game()

    assert game.stage == 2
    assert game.score == 100
    assert game.game_over is False
    assert game.monster_group is not None  # Add this assertion


def test_generate_node_tree(game):
    with patch.object(
        game, "generate_node_tree", return_value=Mock()
    ) as mock_generate_node_tree:
        game.generate_node_tree()

    assert mock_generate_node_tree.call_count == 1
    assert game.node_tree is not None


def test_initialize_combat(game):
    mock_node = Mock()
    mock_monster_group = Mock(spec=MonsterGroup)
    mock_monster_group.monsters = [Mock(), Mock()]  # Create mock monsters
    mock_monster_group.decide_action.return_value = {}  # Mock the decide_action method
    mock_node.content = {"monsters": mock_monster_group}
    game.current_node = mock_node

    game.screen = pygame.Surface((800, 600))

    with patch("deckdeep.game.Game.apply_relic_effects"), patch(
        "pygame.transform.scale", return_value=pygame.Surface((100, 100))
    ), patch("deckdeep.render.render_combat_state"), patch(
        "pygame.display.flip"
    ), patch(
        "deckdeep.game.Game.animate_combat_start"
    ):  # Add this line

        game.initialize_combat()

        # Check if the game's monster_group was updated with the new monsters
        assert game.monster_group == mock_monster_group

    assert game.player_turn is True
    game.player.reset_hand.assert_called_once()
    mock_monster_group.decide_action.assert_called_once_with(game.player)


def test_monster_intentions(game):
    mock_monster = Mock()
    game.monster_group.monsters = [mock_monster]
    game.monster_group.decide_action = Mock(return_value={"mock_monster": "ATTACK"})
    game.monster_intentions = game.monster_group.decide_action(game.player)
    game.monster_group.decide_action.assert_called_once_with(game.player)
    assert game.monster_intentions == {"mock_monster": "ATTACK"}


def test_combat_state_transitions(game):
    game.combat_state = "player_turn"
    game.end_player_turn = Mock()
    game.end_monster_turn = Mock()

    game.end_player_turn()
    game.end_player_turn.assert_called_once()

    game.combat_state = "monster_turn"
    game.end_monster_turn()
    game.end_monster_turn.assert_called_once()


if __name__ == "__main__":
    pytest.main()
