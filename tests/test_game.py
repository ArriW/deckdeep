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
from deckdeep.relic import Relic  # noqa: E402
from deckdeep.status_effect import TriggerType  # noqa: E402


@pytest.fixture
def mock_logger():
    return Mock(spec=GameLogger)


@pytest.fixture
def game(mock_logger):
    with patch("pygame.init"), patch(
        "pygame.display.set_mode", return_value=pygame.Surface((800, 600))
    ), patch("deckdeep.game.GameAssets") as mock_assets, patch(
        "deckdeep.game.Player"
    ), patch(
        "deckdeep.game.MonsterGroup"
    ), patch(
        "deckdeep.game.Node"
    ):
        mock_assets.return_value.background_image = pygame.Surface((800, 600))
        mock_assets.return_value.player = pygame.Surface((50, 50))
        mock_assets.return_value.health_bar = pygame.Surface((100, 10))
        mock_assets.return_value.energy_icon = pygame.Surface((20, 20))
        mock_assets.return_value.parchment_texture = pygame.Surface((100, 100))
        mock_assets.return_value.victory_image = pygame.Surface((800, 600))
        # Add more asset mocks as needed for all assets used in render_victory_state
        mock_assets.return_value.attack_icon = pygame.Surface((20, 20))
        mock_assets.return_value.shield_icon = pygame.Surface((20, 20))
        mock_assets.return_value.heal_icon = pygame.Surface((20, 20))
        mock_assets.return_value.draw_icon = pygame.Surface((20, 20))
        mock_assets.return_value.health_cost = pygame.Surface((20, 20))
        mock_assets.return_value.bleed_icon = pygame.Surface((20, 20))
        mock_assets.return_value.energy_bonus_icon = pygame.Surface((20, 20))
        mock_assets.return_value.health_regain_icon = pygame.Surface((20, 20))
        mock_assets.return_value.weakness_icon = pygame.Surface((20, 20))
        mock_assets.return_value.bolster_icon = pygame.Surface((20, 20))
        mock_assets.return_value.burn_icon = pygame.Surface((20, 20))

        screen = pygame.Surface((800, 600))  # Create a real surface
        game = Game(screen, mock_logger)
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
    monster_group = MonsterGroup()
    mock_monster1 = Mock()
    mock_monster1.is_alive = Mock(return_value=True)
    mock_monster1.execute_action = Mock(return_value="Monster 1 attacked")
    mock_monster2 = Mock()
    mock_monster2.is_alive = Mock(return_value=True)
    mock_monster2.execute_action = Mock(return_value="Monster 2 attacked")

    monster_group.monsters = [mock_monster1, mock_monster2]

    results = monster_group.execute_actions(game.player)

    mock_monster1.execute_action.assert_called_once_with(game.player)
    mock_monster2.execute_action.assert_called_once_with(game.player)

    assert results == ["Monster 1 attacked", "Monster 2 attacked"]


def test_monster_intentions(game):
    monster_group = MonsterGroup()
    mock_monster = Mock()
    mock_monster.decide_action = Mock(return_value="ATTACK")
    monster_group.monsters = [mock_monster]

    intentions = monster_group.decide_action(game.player)

    mock_monster.decide_action.assert_called_once_with(game.player)
    assert intentions == ["ATTACK"]


def test_initialize_combat(game):
    mock_node = Mock()
    monster_group = MonsterGroup()
    mock_monster1 = Mock()
    mock_monster2 = Mock()
    monster_group.monsters = [mock_monster1, mock_monster2]
    mock_node.content = {"monsters": monster_group}
    game.current_node = mock_node

    game.screen = pygame.Surface((800, 600))

    with patch("deckdeep.game.Game.apply_relic_effects"), patch(
        "pygame.transform.scale", return_value=pygame.Surface((100, 100))
    ), patch("deckdeep.render.render_combat_state"), patch(
        "pygame.display.flip"
    ), patch(
        "deckdeep.game.Game.animate_combat_start"
    ):
        game.initialize_combat()
        assert game.monster_group == monster_group

    assert game.player_turn is True
    game.player.reset_hand.assert_called_once()
    assert len(game.monster_intentions) == len(monster_group.monsters)


def test_apply_relic_effects(game):
    mock_relic = Mock(spec=Relic)
    mock_relic.trigger_when = TriggerType.TURN_START
    mock_relic.apply_effect = Mock(return_value="Relic effect applied")
    game.player.relics = [mock_relic]
    game.logger.debug = Mock()

    game.apply_relic_effects(TriggerType.TURN_START)

    mock_relic.apply_effect.assert_called_once_with(game.player, game)
    game.logger.debug.assert_called_with(
        "Applied relic effect: Relic effect applied", category="PLAYER"
    )


def test_save_and_load_game(game):
    mock_player_data = {
        "name": "TestPlayer",
        "health": 80,
        "max_health": 100,
        "symbol": "@",
        "shield": 0,
        "bonus_damage": 0,
        "energy": 3,
        "max_energy": 3,
        "hand_limit": 7,
        "deck": [],
        "hand": [],
        "exhaust_pile": [],
        "discard_pile": [],
        "size": (50, 50),
        "shake": 0,
        "health_gain_on_skip": 5,
        "cards_drawn_per_turn": 5,
        "hp_regain_per_level": 10,
        "status_effects": {"effects": []},
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
        "content": {"monsters": mock_monster_group},
        "children": [
            {
                "node_type": "combat",
                "stage": 1,
                "level": 2,
                "true_level": 2,
                "content": {"monsters": mock_monster_group},
                "children": [],
            }
        ],
    }

    game.player.to_dict = Mock(return_value=mock_player_data)
    game.node_tree = Node.from_dict(mock_node_data)
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
            "current_node_path": [0],
            "stage": 2,
            "score": 100,
            "game_over": False,
        }
        mock_monster_group_from_dict.return_value = Mock()
        game.save_game()
        game.load_game()

    assert game.stage == 2
    assert game.score == 100
    assert game.game_over is False
    assert game.monster_group is not None


def test_generate_node_tree(game):
    with patch.object(
        game, "generate_node_tree", return_value=Mock()
    ) as mock_generate_node_tree:
        game.generate_node_tree()

    assert mock_generate_node_tree.call_count == 1
    assert game.node_tree is not None


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
