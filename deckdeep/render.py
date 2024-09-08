import pygame
import pygame.gfxdraw
import random
from collections import Counter
from typing import List, TYPE_CHECKING

from deckdeep.assets import GameAssets
from deckdeep.card import Card
from deckdeep.config import (
    BEIGE,
    BLACK,
    BLUE,
    BUTTON_HEIGHT,
    BUTTON_WIDTH,
    CARD_FONT,
    CARD_HEIGHT,
    CARD_SPACING,
    CARD_WIDTH,
    END_TURN_BUTTON_X,
    END_TURN_BUTTON_Y,
    FONT,
    GRAY,
    GREEN,
    ICON_SIZE,
    KEYBINDS,
    PLAYER_SIZE,
    PURPLE,
    RED,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SMALL_FONT,
    VIEW_DECK_BUTTON_X,
    VIEW_DECK_BUTTON_Y,
    WHITE,
    YELLOW,
    scale,
)
from deckdeep.monster import IconType
from deckdeep.monster_group import MonsterGroup
from deckdeep.player import Player
from deckdeep.relic import Relic

# Imports only for type checking to avoid circular imports
if TYPE_CHECKING:
    from deckdeep.game import Node


def get_key_name(key: int) -> str:
    return pygame.key.name(key).upper()


def render_text(
    screen: pygame.Surface,
    text: str,
    x: int,
    y: int,
    color=BLACK,
    font=FONT,
    circle=False,
    outline=False,
    outline_color=BLACK,
    shadow=False,
    shadow_color=(50, 50, 50, 128),
):
    if shadow:
        shadow_offset = scale(1)
        render_text(
            screen,
            text,
            x + shadow_offset,
            y + shadow_offset,
            color=shadow_color,
            font=font,
            outline=False,
        )

    if outline:
        for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            render_text(
                screen,
                text,
                x + dx,
                y + dy,
                color=outline_color,
                font=font,
                outline=False,
            )

    text_surface = font.render(text, True, color)
    if circle:
        text_rect = text_surface.get_rect()
        circle_radius = max(text_rect.width, text_rect.height) * 1.3 // 2
        circle_center = (x + text_rect.width // 2, y + text_rect.height // 2)
        circle_surface = pygame.Surface(
            (circle_radius * 2, circle_radius * 2), pygame.SRCALPHA
        )
        pygame.draw.circle(
            circle_surface,
            (255, 255, 255, 128),
            (circle_radius, circle_radius),
            circle_radius,
        )
        screen.blit(
            circle_surface,
            (circle_center[0] - circle_radius, circle_center[1] - circle_radius),
        )
    screen.blit(text_surface, (x, y))


def render_text_in_icon(
    screen: pygame.Surface, text: str, x: int, y: int, icon, color=BLACK, font=FONT
):
    screen.blit(icon, (x, y))

    render_text(
        screen,
        text,
        x + ICON_SIZE - scale(23),
        y + scale(7),
        color=color,
        font=font,
        outline=True,
        shadow=True,
    )


def render_text_with_background(
    screen: pygame.Surface,
    text: str,
    x: int,
    y: int,
    font,
    text_color=BLACK,
    background_color=WHITE,
    max_width=None,
):
    words = text.split()
    lines = []
    current_line: List[str] = []

    for word in words:
        test_line = " ".join(current_line + [word])
        test_width = font.size(test_line)[0]
        if max_width and test_width > max_width:
            lines.append(" ".join(current_line))
            current_line = [word]
        else:
            current_line.append(word)

    if current_line:
        lines.append(" ".join(current_line))

    for i, line in enumerate(lines):
        text_surface = font.render(line, True, text_color)
        if background_color:
            background_surface = pygame.Surface(text_surface.get_size())
            background_surface.fill(background_color)
            screen.blit(background_surface, (x, y + i * font.get_linesize()))
        screen.blit(text_surface, (x, y + i * font.get_linesize()))


def render_card(
    screen: pygame.Surface,
    card: Card,
    x: int,
    y: int,
    is_selected: bool,
    assets: GameAssets,
    player_energy: int,
    player_max_energy: int,
    player_bonus_damage: int,
    player_strength: int,
    hotkey=None,
    opacity=255,
):
    x_offset = ICON_SIZE + scale(16)
    x_anchor = scale(15)
    y_offset = ICON_SIZE + scale(3)
    y_text_offset = scale(5)

    # Create a new surface for the card
    card_surface = pygame.Surface((CARD_WIDTH, CARD_HEIGHT), pygame.SRCALPHA)

    # 1. Bottom layer: Parchment texture
    card_surface.blit(assets.parchment_texture, (0, 0))

    # # 2. Middle layer: Rarity hue
    # rarity_colors = {
    #     Rarity.COMMON: None,
    #     Rarity.UNCOMMON: (0, 255, 0, 40),
    #     Rarity.RARE: (0, 0, 255, 40),
    #     Rarity.UNIQUE: (128, 0, 128, 40),
    #     Rarity.LEGENDARY: (255, 0, 0, 40),
    # }

    # if card.rarity in rarity_colors and rarity_colors[card.rarity] is not None:
    #     color_surface = pygame.Surface((CARD_WIDTH, CARD_HEIGHT), pygame.SRCALPHA)
    #     color_surface.fill(rarity_colors[card.rarity])
    #     card_surface.blit(color_surface, (0, 0))

    # 3. Top layer: Card content (name, icons, text)
    name_surface = CARD_FONT.render(card.name, True, BLACK)
    name_x = (CARD_WIDTH - name_surface.get_width()) // 2
    card_surface.blit(name_surface, (name_x, scale(10)))
    current_y = y_offset + scale(15)

    icon_map = {
        "damage": (
            assets.attack_icon,
            f"{card.calculate_total_damage(player_bonus_damage, player_strength)}{' (AOE)' if card.targets_all else ''}",
        ),
        "bonus_damage": (assets.dice_icon, f"{card.bonus_damage}"),
        "healing": (assets.heal_icon, f"{card.healing}"),
        "shield": (assets.shield_icon, f"{card.shield}"),
        "card_draw": (assets.draw_icon, f"{card.card_draw}"),
        "health_cost": (assets.health_cost, f"-{card.health_cost}"),
        "bleed": (assets.bleed_icon, f"{card.bleed}"),
        "energy_bonus": (assets.energy_bonus_icon, f"+{card.energy_bonus}"),
        "health_regain": (assets.health_regain_icon, f"+{card.health_regain}"),
        "weakness": (assets.weakness_icon, f"{card.weakness}"),
        "bolster": (assets.bolster_icon, f"{card.bolster}"),
        "burn": (assets.burn_icon, f"{card.burn}"),
    }

    for attr, (icon, text) in icon_map.items():
        if getattr(card, attr, 0) > 0:
            icon_surface = icon.copy()
            icon_y = current_y

            if attr == "damage" and card.num_attacks > 1:
                # Render multiple attack icons
                overlap = ICON_SIZE // 3  # Reduced overlap for better visibility
                total_width = x_anchor + (card.num_attacks - 1) * overlap + ICON_SIZE
                for i in range(card.num_attacks):
                    card_surface.blit(icon_surface, (x_anchor + i * overlap, icon_y))

                # Dynamically calculate text position
                text_width = CARD_FONT.size(text)[0]
                text_x = max(
                    x_offset, total_width + scale(5)
                )  # Ensure minimum x_offset
                if text_x + text_width > CARD_WIDTH - scale(10):
                    text_x = (
                        CARD_WIDTH - text_width - scale(10)
                    )  # Adjust if text would overflow

                render_text(
                    card_surface,
                    str(int(text) // card.num_attacks),
                    text_x,
                    icon_y + y_text_offset,
                    font=CARD_FONT,
                    color=BLACK,
                )
            else:
                card_surface.blit(icon_surface, (x_anchor, icon_y))
                render_text(
                    card_surface,
                    text,
                    x_offset,
                    icon_y + y_text_offset,
                    font=CARD_FONT,
                    color=BLACK,
                )
            current_y += y_offset

    energy_x = CARD_WIDTH - round(1.25 * ICON_SIZE)
    energy_y = CARD_HEIGHT - round(1.25 * ICON_SIZE)

    if player_energy >= card.energy_cost.value:
        energy_color = GREEN
    elif player_max_energy >= card.energy_cost.value:
        energy_color = RED
    else:
        energy_color = RED

    render_text_in_icon(
        card_surface,
        f"{card.energy_cost.value}",
        energy_x,
        energy_y,
        assets.energy_icon,
        color=energy_color,
        font=CARD_FONT,
    )

    if hotkey is not None:
        render_text(
            card_surface,
            f"{get_key_name(hotkey)}",
            x_anchor,
            CARD_HEIGHT - x_offset,
            font=CARD_FONT,
            color=BLACK,
        )

    # Apply opacity to the entire card surface
    card_surface.set_alpha(opacity)

    # Blit the card surface to the screen
    screen.blit(card_surface, (x, y))

    # Draw border
    border_color = YELLOW if is_selected else BLACK
    pygame.draw.rect(screen, border_color, (x, y, CARD_WIDTH, CARD_HEIGHT), 2)

    return x, y


def render_button(
    screen: pygame.Surface, text: str, x: int, y: int, width: int, height: int
):
    pygame.draw.rect(screen, GRAY, (x, y, width, height))
    pygame.draw.rect(screen, BLACK, (x, y, width, height), 2)
    render_text(screen, text, x + scale(10), y + scale(10))


def render_health_bar(
    screen: pygame.Surface,
    x: int,
    y: int,
    width: int,
    height: int,
    current,
    maximum,
    color,
    assets: GameAssets,
    shield=0,
):
    current_value = current.value if hasattr(current, "value") else current
    maximum_value = maximum.value if hasattr(maximum, "value") else maximum
    current_width = int(width * (current_value / maximum_value))

    # Draw rounded rectangle for the border
    pygame.draw.rect(
        screen,
        BLACK,
        (x - scale(1), y - scale(1), width + scale(2), height + scale(2)),
        border_radius=scale(5),
    )

    # Draw rounded rectangle for the background
    pygame.draw.rect(screen, GRAY, (x, y, width, height), border_radius=scale(5))

    # Draw rounded rectangle for the current health/energy
    pygame.draw.rect(
        screen, color, (x, y, current_width, height), border_radius=scale(5)
    )

    # Draw parchment texture overlay
    if assets:
        parchment = assets.parchment_texture
        scaled_parchment = pygame.transform.scale(parchment, (width, height))
        screen.blit(scaled_parchment, (x, y), special_flags=pygame.BLEND_MULT)

    # Draw ticks every 10%
    for i in range(1, 10):
        tick_x = x + (width * i // 10)
        pygame.draw.line(screen, BLACK, (tick_x, y), (tick_x, y + height), 1)

    if shield > 0:
        shield_width = int(width * (shield / maximum_value))
        s = pygame.Surface((shield_width, height))
        s.set_alpha(128)
        s.fill(BLUE)
        screen.blit(s, (x + current_width - shield_width, y))

    # health_text = f"{current}/{maximum}"
    health_text = str(current_value)
    if shield > 0:
        health_text += f" (+{shield})"
    text_x = x + (width - SMALL_FONT.size(health_text)[0]) // 2
    render_text(
        screen,
        health_text,
        text_x,
        y + scale(2),
        color=WHITE,
        font=SMALL_FONT,
        outline=True,
    )


def render_status_effects(
    screen: pygame.Surface, x: int, y: int, status_effects: List, assets: GameAssets
):
    icon_spacing = scale(35)
    effect_icons = {
        "Bleed": (assets.bleed_icon, PURPLE),
        "HealthRegain": (assets.health_regain_icon, PURPLE),
        "EnergyBonus": (assets.energy_bonus_icon, PURPLE),
        "PlayerBonus": (assets.attack_icon, PURPLE),
        "Strength": (assets.strength_icon, PURPLE),
        "Weakness": (assets.weakness_icon, RED),
        "Bolster": (assets.bolster_icon, BLUE),
        "Burn": (assets.burn_icon, RED),
    }
    for effect in status_effects:
        effect_name = effect.__class__.__name__
        if effect_name in effect_icons:
            icon, color = effect_icons[effect_name]
            screen.blit(icon, (x, y))
            render_text(
                screen,
                str(effect.value),
                x + round(ICON_SIZE / 2) - scale(3),
                y - round(ICON_SIZE / 2) - scale(4),
                color=color,
                font=FONT,
                circle=True,
            )
            x += icon_spacing


def render_player(
    screen: pygame.Surface,
    player: Player,
    assets: GameAssets,
    monster_center_y: int,
    animation_progress: float = 1.0,
):
    player_image = pygame.transform.scale(assets.player, (PLAYER_SIZE, PLAYER_SIZE))

    target_x = scale(120)
    start_x = -PLAYER_SIZE
    current_x = start_x + (target_x - start_x) * animation_progress

    y = monster_center_y - PLAYER_SIZE // 2
    offset = random.randint(-player.shake, player.shake)

    # Render status effects above the player
    status_effects = player.status_effects.effects.copy()

    # HACK should make these more formal status effects so we don't have to attempt them like this
    if player.bonus_damage > 0:
        status_effects.append(type("PlayerBonus", (), {"value": player.bonus_damage})())
    if player.strength > 0:
        status_effects.append(type("Strength", (), {"value": player.strength})())
    render_status_effects(screen, int(current_x), y - scale(50), status_effects, assets)

    # Render player image with death animation if applicable
    if player.is_dying:
        death_progress = min(
            1.0, (pygame.time.get_ticks() - player.death_start_time) / 1000
        )
        opacity = int(255 * (1 - death_progress))
        render_with_opacity(
            screen, player_image, int(current_x) + offset, y + offset, opacity
        )
    else:
        screen.blit(player_image, (int(current_x) + offset, y + offset))

    # Render health bar below the player
    health_bar_width = PLAYER_SIZE
    health_bar_height = scale(20)
    render_health_bar(
        screen,
        int(current_x),
        y + PLAYER_SIZE + scale(10),
        health_bar_width,
        health_bar_height,
        player.health,
        player.max_health,
        GREEN,
        assets,
        player.shield,
    )

    # Render energy bar below the health bar
    render_health_bar(
        screen,
        int(current_x),
        y + PLAYER_SIZE + scale(35),
        health_bar_width,
        health_bar_height,
        player.energy,
        player.max_energy,
        BLUE,
        assets,
        0,
    )

    if player.shake > 0:
        player.shake -= 1


def get_intention_icons(
    intention_icon_types: List[IconType], assets: GameAssets
) -> List[pygame.Surface]:

    icon_map = {
        IconType.ATTACK: assets.attack_icon,
        IconType.DEFEND: assets.shield_icon,
        IconType.BUFF: assets.strength_icon,
        IconType.BLEED: assets.bleed_icon,
        IconType.HEAL: assets.heal_icon,
        IconType.MAGIC: assets.energy_icon,
        IconType.UNKNOWN: assets.draw_icon,
    }
    return [
        icon_map.get(icon_type, assets.draw_icon) for icon_type in intention_icon_types
    ]


def render_monsters(
    screen: pygame.Surface,
    monster_group: MonsterGroup,
    assets: GameAssets,
    animation_progress: float = 1.0,
):
    num_monsters = len(monster_group.monsters)
    monsters_per_row = 3
    num_rows = (num_monsters + monsters_per_row - 1) // monsters_per_row

    monster_size = PLAYER_SIZE
    monster_spacing = scale(50)

    total_height = num_rows * (monster_size + monster_spacing) - monster_spacing
    start_y = (SCREEN_HEIGHT - total_height) // 2 - monster_size

    for row in range(num_rows):
        start_index = row * monsters_per_row
        end_index = min((row + 1) * monsters_per_row, num_monsters)
        monsters_in_row = end_index - start_index

        row_width = (
            monsters_in_row * monster_size + (monsters_in_row - 1) * monster_spacing
        )
        target_start_x = SCREEN_WIDTH - scale(120) - row_width
        start_start_x = SCREEN_WIDTH
        current_start_x = (
            start_start_x + (target_start_x - start_start_x) * animation_progress
        )

        for i, monster in enumerate(monster_group.monsters[start_index:end_index]):
            monster_image = pygame.transform.scale(
                GameAssets.load_and_scale_ui(
                    monster.image_path, (monster_size, monster_size)
                ),
                (monster_size, monster_size),
            )
            x = int(current_start_x + i * (monster_size + monster_spacing))
            y = start_y + row * (monster_size + monster_spacing)
            offset = random.randint(-monster.shake, monster.shake)

            # Render status effects above the monster
            render_status_effects(
                screen, x, y - scale(30), monster.status_effects.effects, assets
            )

            # Render monster image with death animation if applicable
            if monster.is_dying:
                death_progress = min(
                    1.0, (pygame.time.get_ticks() - monster.death_start_time) / 1000
                )
                opacity = int(255 * (1 - death_progress))
                render_with_opacity(
                    screen, monster_image, x + offset, y + offset, opacity
                )
            else:
                screen.blit(monster_image, (x + offset, y + offset))

            # Render health bar below the monster
            health_bar_width = monster_size
            health_bar_height = scale(20)
            render_health_bar(
                screen,
                x,
                y + monster_size + scale(10),
                health_bar_width,
                health_bar_height,
                monster.health,
                monster.max_health,
                RED,
                assets,
                monster.shields,
            )

            try:
                # Render yellow frame for selected monster
                if monster.selected:
                    frame_padding = scale(5)
                    pygame.draw.rect(
                        screen,
                        YELLOW,
                        (
                            x - frame_padding,
                            y - frame_padding,
                            monster_size + 2 * frame_padding,
                            monster_size + 2 * frame_padding,
                        ),
                        3,
                    )

                # Render monster damage in top right corner of the frame
                damage_x = x + scale(12)
                damage_y = y + scale(12)
                render_text(
                    screen,
                    str(monster.damage),
                    damage_x,
                    damage_y,
                    color=BLACK,
                    font=FONT,
                    circle=True,
                    outline_color=BLACK,
                )

                # Render monster intention icons
                intention_icons = get_intention_icons(
                    monster.intention_icon_types, assets
                )
                icon_width = ICON_SIZE
                total_width = len(intention_icons) * icon_width
                icon_start_x = x + (monster_size - total_width) // 2
                icon_y = y + monster_size - ICON_SIZE - scale(5)

                for j, icon in enumerate(intention_icons):
                    screen.blit(icon, (icon_start_x + j * icon_width, icon_y))

                if monster.shake > 0:
                    monster.shake -= 1
            except AttributeError as e:
                print(
                    f"Error rendering monster intention icons, maybe game just loaded? {e}"
                )

    # Return the center y-coordinate of the monster group
    return start_y + total_height // 2


def render_combat_state(
    screen: pygame.Surface,
    player: Player,
    monster_group: MonsterGroup,
    dungeon_level: str,
    score: int,
    selected_card: int,
    assets: GameAssets,
    played_cards: List[Card] = [],
    animation_progress: float = 1.0,
):
    screen.blit(assets.background_image, (0, 0))

    # Render parchment texture at the top
    header_height = scale(50)
    parchment = pygame.transform.scale(
        assets.parchment_texture, (SCREEN_WIDTH, header_height)
    )
    screen.blit(parchment, (0, 0))

    # Render score in the top left
    render_text(screen, f"Score: {score}", scale(10), scale(15), color=BLACK)

    # Render dungeon level in the top center
    level_text = f"Level: {dungeon_level}"
    level_width = FONT.size(level_text)[0]
    render_text(
        screen, level_text, (SCREEN_WIDTH - level_width) // 2, scale(15), color=BLACK
    )

    monster_center_y = render_monsters(
        screen, monster_group, assets, animation_progress
    )
    render_player(screen, player, assets, monster_center_y, animation_progress)

    s = pygame.Surface((SCREEN_WIDTH, CARD_HEIGHT + scale(40)))
    s.set_alpha(128)
    s.fill((100, 100, 100))
    screen.blit(s, (0, SCREEN_HEIGHT - CARD_HEIGHT - scale(40)))

    card_start_x = (
        SCREEN_WIDTH - (len(player.hand) * (CARD_WIDTH + CARD_SPACING) - CARD_SPACING)
    ) // 2
    combat_keys = next(iter(KEYBINDS["Event"].keys()))
    num_keys = [pygame.key.key_code(k) for k in combat_keys.split(", ")]
    for i, card in enumerate(player.hand):
        card.x, card.y = render_card(
            screen,
            card,
            card_start_x + i * (CARD_WIDTH + CARD_SPACING),
            SCREEN_HEIGHT - CARD_HEIGHT - scale(20),
            i == selected_card,
            assets,
            player.energy.value,
            player.max_energy.value,
            player.bonus_damage,
            player.strength,
            hotkey=num_keys[i] if i < len(num_keys) else None,
        )

    # Render played cards with animation
    if played_cards:
        for card in played_cards:
            if card.is_animating:
                render_card(
                    screen,
                    card,
                    card.x,
                    card.y,
                    False,
                    assets,
                    player.energy.value,
                    player.max_energy.value,
                    player.bonus_damage,
                    player.strength,
                    opacity=card.opacity,
                )
                card.update_animation()
                if not card.is_animating:  # Check if the animation is complete
                    card.reset_animation()  # Reset animation properties for reuse

    render_button(
        screen,
        "End Turn",
        END_TURN_BUTTON_X,
        END_TURN_BUTTON_Y,
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
    )
    render_button(
        screen,
        "View Deck",
        VIEW_DECK_BUTTON_X,
        VIEW_DECK_BUTTON_Y,
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
    )

    pygame.display.flip()


def render_victory_state(
    screen: pygame.Surface,
    score: int,
    new_cards: List[Card],
    selected_card: int,
    assets: GameAssets,
    player: Player,
):
    screen.blit(assets.victory_image, (0, 0))
    # screen.fill(BLACK)
    header_height = scale(200)
    s = pygame.Surface((SCREEN_WIDTH, header_height))
    s.set_alpha(128)
    s.fill(BEIGE)
    screen.blit(s, (0, 0))

    render_text(screen, "Victory!", SCREEN_WIDTH // 2 - 50, 50)
    render_text(screen, f"Score: {score}", SCREEN_WIDTH // 2 - 50, 100)
    render_text(
        screen, "Select a card to add to your deck:", SCREEN_WIDTH // 2 - 150, 150
    )
    render_text(
        screen,
        "Press number keys to select a card, or #4 to skip and gain +5 max HP",
        SCREEN_WIDTH // 2 - 250,
        175,
    )

    victory_keys = next(iter(KEYBINDS["Victory Screen"].keys()))
    num_keys = [pygame.key.key_code(k) for k in victory_keys.split(", ")]
    for i, card in enumerate(new_cards):
        render_card(
            screen,
            card,
            scale(250) + i * (CARD_WIDTH + CARD_SPACING),
            scale(250),
            i == selected_card,
            assets,
            player.energy.value,
            player.max_energy.value,
            player.bonus_damage,
            player.strength,
            hotkey=num_keys[i] if i < len(num_keys) else None,
        )

    render_text(
        screen,
        f"{get_key_name(num_keys[-1])}: Skip",
        scale(250) + 3 * (CARD_WIDTH + CARD_SPACING),
        scale(250),
        color=WHITE,
    )

    render_health_bar(
        screen,
        scale(50),
        scale(50),
        scale(200),
        scale(20),
        player.health,
        player.max_health,
        GREEN,
        assets,
        0,
    )
    render_health_bar(
        screen,
        scale(50),
        scale(70),
        scale(200),
        scale(20),
        player.energy,
        player.max_energy,
        BLUE,
        assets,
        0,
    )

    pygame.display.flip()


def render_start_screen(screen: pygame.Surface, assets: GameAssets):
    screen.blit(assets.start_screen_image, (0, 0))
    render_text(
        screen, "Press any key to start", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 50
    )
    pygame.display.flip()


def render_game_over_screen(screen: pygame.Surface, score: int, assets: GameAssets):
    screen.blit(assets.game_over_image, (0, 0))
    render_text(
        screen, f"Final Score: {score}", SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT - 100
    )
    render_text(
        screen, "Press any key to continue", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 50
    )
    pygame.display.flip()


def render_menu(
    screen: pygame.Surface, options: List[str], selected: int, assets: GameAssets
):
    screen.blit(assets.background_image, (0, 0))

    menu_width = scale(300)
    menu_height = scale(50) * len(options) + scale(20)
    menu_x = (SCREEN_WIDTH - menu_width) // 2
    menu_y = (SCREEN_HEIGHT - menu_height) // 2
    pygame.draw.rect(screen, BEIGE, (menu_x, menu_y, menu_width, menu_height))
    pygame.draw.rect(screen, BLACK, (menu_x, menu_y, menu_width, menu_height), 2)

    for i, option in enumerate(options):
        text_color = YELLOW if i == selected else BLACK
        render_text(
            screen,
            f"#{i + 1}: {option}",
            menu_x + scale(20),
            menu_y + scale(20) + i * scale(50),
            color=text_color,
        )

    pygame.display.flip()


def render_text_event(
    screen: pygame.Surface,
    event_name: str,
    event_description: str,
    options: List[str],
    assets: GameAssets,
    player: Player,
):
    # Render event image
    event_image = assets.load_event_image(event_name)
    screen.blit(event_image, (0, 0))

    # Render description parchment
    description_parchment = pygame.transform.scale(
        assets.parchment_texture,
        (SCREEN_WIDTH // 2 - scale(20), SCREEN_HEIGHT // 3 - scale(20)),
    )
    screen.blit(description_parchment, (scale(10), SCREEN_HEIGHT * 2 // 3 + scale(10)))

    # Render options parchment
    options_parchment = pygame.transform.scale(
        assets.parchment_texture,
        (SCREEN_WIDTH // 2 - scale(20), SCREEN_HEIGHT // 3 - scale(20)),
    )
    screen.blit(
        options_parchment,
        (SCREEN_WIDTH // 2 + scale(10), SCREEN_HEIGHT * 2 // 3 + scale(10)),
    )

    # Render event description
    render_text_with_background(
        screen,
        event_description,
        scale(20),
        SCREEN_HEIGHT * 2 // 3 + scale(20),
        SMALL_FONT,
        text_color=BLACK,
        background_color=None,
        max_width=SCREEN_WIDTH // 2 - scale(40),
    )

    # Render options
    key_mapping = ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"]
    for i, option in enumerate(options):
        if i < len(key_mapping):
            render_text(
                screen,
                f"{key_mapping[i]}: {option}",
                SCREEN_WIDTH // 2 + scale(20),
                SCREEN_HEIGHT * 2 // 3 + scale(20) + i * scale(30),
                color=BLACK,
                font=SMALL_FONT,
            )

    # Render player stats
    render_health_bar(
        screen,
        scale(50),
        scale(50),
        scale(200),
        scale(20),
        player.health,
        player.max_health,
        GREEN,
        assets,
        0,
    )
    render_health_bar(
        screen,
        scale(50),
        scale(70),
        scale(200),
        scale(20),
        player.energy,
        player.max_energy,
        BLUE,
        assets,
        0,
    )

    pygame.display.flip()


def render_node_selection(
    screen: pygame.Surface, nodes: List["Node"], selected: int, assets: GameAssets
):
    screen.blit(assets.background_image, (0, 0))

    render_text(
        screen, "Choose your next path:", SCREEN_WIDTH // 2 - scale(100), scale(50)
    )

    node_width = scale(150)
    node_height = scale(100)
    node_spacing = scale(50)
    total_width = len(nodes) * node_width + (len(nodes) - 1) * node_spacing
    start_x = (SCREEN_WIDTH - total_width) // 2

    for i, node in enumerate(nodes):
        node_x = start_x + i * (node_width + node_spacing)
        node_y = SCREEN_HEIGHT // 2 - node_height // 2

        color = YELLOW if i == selected else WHITE
        pygame.draw.rect(screen, color, (node_x, node_y, node_width, node_height))
        pygame.draw.rect(screen, BLACK, (node_x, node_y, node_width, node_height), 2)

        node_type_text = node.node_type.capitalize()
        render_text(screen, node_type_text, node_x + scale(10), node_y + scale(10))
        render_text(
            screen, f"Level {node.level}", node_x + scale(10), node_y + scale(50)
        )
        hotkey_list = [
            get_key_name(pygame.K_q),
            get_key_name(pygame.K_w),
            get_key_name(pygame.K_e),
            get_key_name(pygame.K_r),
            get_key_name(pygame.K_t),
            get_key_name(pygame.K_y),
            get_key_name(pygame.K_u),
            get_key_name(pygame.K_i),
            get_key_name(pygame.K_o),
            get_key_name(pygame.K_p),
        ]
        render_text(
            screen, hotkey_list[i], node_x + scale(10), node_y + node_height - scale(30)
        )

    render_text(
        screen,
        "Press number keys to select a path",
        SCREEN_WIDTH // 2 - scale(150),
        SCREEN_HEIGHT - scale(50),
    )

    pygame.display.flip()


def render_deck_view(
    screen: pygame.Surface,
    deck: List[Card],
    current_page: int,
    total_pages: int,
    assets: GameAssets,
    player: Player,
):
    screen.blit(assets.background_image, (0, 0))

    render_text(screen, "Full Deck View", SCREEN_WIDTH // 2 - scale(50), scale(20))
    render_text(
        screen, f"Total Cards: {len(deck)}", SCREEN_WIDTH - scale(150), scale(20)
    )
    render_text(
        screen,
        "Use Left/Right arrows to change pages, Esc to close",
        SCREEN_WIDTH // 2 - scale(200),
        SCREEN_HEIGHT - scale(30),
    )

    cards_per_row = 5
    cards_per_column = 3
    cards_per_page = cards_per_row * cards_per_column
    card_spacing_x = scale(20)
    card_spacing_y = scale(20)
    start_x = (
        SCREEN_WIDTH
        - (cards_per_row * CARD_WIDTH + (cards_per_row - 1) * card_spacing_x)
    ) // 2
    start_y = scale(80)

    current_page = max(0, min(current_page, total_pages - 1))

    start_index = current_page * cards_per_page
    end_index = min(start_index + cards_per_page, len(deck))

    for i, card in enumerate(deck[start_index:end_index]):
        row = i // cards_per_row
        col = i % cards_per_row
        x = start_x + col * (CARD_WIDTH + card_spacing_x)
        y = start_y + row * (CARD_HEIGHT + card_spacing_y)

        render_card(
            screen,
            card,
            x,
            y,
            False,
            assets,
            player.energy.value,
            player.max_energy.value,
            player.bonus_damage,
            player.strength,
        )

    # Render page information
    render_text(
        screen,
        f"Page {current_page + 1} of {total_pages}",
        SCREEN_WIDTH // 2 - scale(50),
        SCREEN_HEIGHT - scale(60),
    )

    pygame.display.flip()

    return current_page


def render_relic_selection(
    screen: pygame.Surface,
    new_relics: List[Relic],
    selected_relic: int,
    assets: GameAssets,
):
    screen.fill(BLACK)
    header_height = scale(200)
    s = pygame.Surface((SCREEN_WIDTH, header_height))
    s.set_alpha(128)
    s.fill(BEIGE)
    screen.blit(s, (0, 0))

    render_text(screen, "Select a Relic", SCREEN_WIDTH // 2 - scale(50), scale(50))
    render_text(
        screen,
        "Press number keys to select a relic, or SPACE to skip",
        SCREEN_WIDTH // 2 - scale(250),
        scale(100),
    )

    relic_width = scale(200)
    relic_height = scale(150)
    relic_spacing = scale(50)
    total_width = len(new_relics) * relic_width + (len(new_relics) - 1) * relic_spacing
    start_x = (SCREEN_WIDTH - total_width) // 2
    start_y = scale(250)

    relic_keys = next(iter(KEYBINDS["Relic Selection"].keys()))
    num_keys = [pygame.key.key_code(k) for k in relic_keys.split(", ")]
    for i, relic in enumerate(new_relics):
        relic_x = start_x + i * (relic_width + relic_spacing)
        relic_y = start_y

        color = YELLOW if i == selected_relic else WHITE
        pygame.draw.rect(screen, color, (relic_x, relic_y, relic_width, relic_height))
        pygame.draw.rect(
            screen, BLACK, (relic_x, relic_y, relic_width, relic_height), 2
        )

        render_text(
            screen,
            relic.name,
            relic_x + scale(10),
            relic_y + scale(10),
            font=SMALL_FONT,
        )

        words = relic.description.split()
        lines = []
        current_line: List[str] = []
        for word in words:
            test_line = " ".join(current_line + [word])
            if SMALL_FONT.size(test_line)[0] <= relic_width - scale(20):
                current_line.append(word)
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
        lines.append(" ".join(current_line))

        for j, line in enumerate(lines):
            render_text(
                screen,
                line,
                relic_x + scale(10),
                relic_y + scale(40) + j * scale(20),
                font=SMALL_FONT,
            )

        render_text(
            screen,
            f"{get_key_name(num_keys[i]) if i < len(num_keys) else ''}",
            relic_x + relic_width - scale(30),
            relic_y + relic_height - scale(30),
            font=SMALL_FONT,
        )

    render_text(
        screen,
        f"{get_key_name(num_keys[-1])}: Skip",
        start_x + 3 * (relic_width + relic_spacing),
        start_y,
        font=SMALL_FONT,
    )

    pygame.display.flip()


def render_relic_view(screen: pygame.Surface, relics: List[Relic], assets: GameAssets):
    screen.blit(assets.background_image, (0, 0))

    render_text(screen, "Relic View", SCREEN_WIDTH // 2 - scale(50), scale(20))
    render_text(
        screen, f"Total Relics: {len(relics)}", SCREEN_WIDTH - scale(150), scale(20)
    )
    render_text(
        screen,
        "Press Esc or R to close",
        SCREEN_WIDTH // 2 - scale(100),
        SCREEN_HEIGHT - scale(30),
    )

    relic_width = scale(200)
    relic_height = scale(150)
    relic_spacing_x = scale(20)
    relic_spacing_y = scale(20)
    relics_per_row = 4
    start_x = (
        SCREEN_WIDTH
        - (relics_per_row * relic_width + (relics_per_row - 1) * relic_spacing_x)
    ) // 2
    start_y = scale(80)

    relic_counts = Counter(relic.name for relic in relics)

    for i, (relic_name, count) in enumerate(relic_counts.items()):
        row = i // relics_per_row
        col = i % relics_per_row
        x = start_x + col * (relic_width + relic_spacing_x)
        y = start_y + row * (relic_height + relic_spacing_y)

        relic = next(relic for relic in relics if relic.name == relic_name)

        pygame.draw.rect(screen, WHITE, (x, y, relic_width, relic_height))
        pygame.draw.rect(screen, BLACK, (x, y, relic_width, relic_height), 2)

        render_text(screen, relic.name, x + scale(10), y + scale(10), font=SMALL_FONT)
        render_text(
            screen, f"Count: {count}", x + scale(10), y + scale(30), font=SMALL_FONT
        )

        words = relic.description.split()
        lines = []
        current_line: List[str] = []
        for word in words:
            test_line = " ".join(current_line + [word])
            if SMALL_FONT.size(test_line)[0] <= relic_width - scale(20):
                current_line.append(word)
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
        lines.append(" ".join(current_line))

        for j, line in enumerate(lines):
            render_text(
                screen,
                line,
                x + scale(10),
                y + scale(50) + j * scale(20),
                font=SMALL_FONT,
            )

    pygame.display.flip()


def handle_card_selection(full_deck: List[Card], assets: GameAssets, player: Player):
    selected_index = 0
    clock = pygame.time.Clock()
    screen = pygame.display.get_surface()

    while True:
        render_card_selection(
            screen,
            sorted(full_deck, key=lambda card: (card.energy_cost, card.name)),
            selected_index,
            assets,
            player,
        )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_k:
                    selected_index = max(0, selected_index - 1)
                elif event.key == pygame.K_j:
                    selected_index = min(len(full_deck) - 1, selected_index + 1)
                elif event.key == pygame.K_SPACE:
                    return selected_index

        clock.tick(30)


def render_card_selection(
    screen: pygame.Surface,
    full_deck: List[Card],
    selected_index: int,
    assets: GameAssets,
    player: Player,
):
    screen.blit(assets.background_image, (0, 0))

    # Render parchment texture at the top
    header_height = scale(50)
    parchment = pygame.transform.scale(
        assets.parchment_texture, (SCREEN_WIDTH, header_height)
    )
    screen.blit(parchment, (0, 0))

    render_text(
        screen,
        "Choose a card. (navigate with K & J and select with SPACE)",
        scale(20),
        scale(15),
        color=BLACK,
    )

    card_list_width = scale(400)
    card_list_height = SCREEN_HEIGHT - header_height - scale(60)
    card_list_x = scale(20)
    card_list_y = header_height + scale(20)

    pygame.draw.rect(
        screen, BEIGE, (card_list_x, card_list_y, card_list_width, card_list_height)
    )
    pygame.draw.rect(
        screen, BLACK, (card_list_x, card_list_y, card_list_width, card_list_height), 2
    )

    visible_cards = 20
    start_index = max(0, min(selected_index, len(full_deck) - visible_cards))

    for i, card in enumerate(full_deck[start_index : start_index + visible_cards]):
        color = RED if i + start_index == selected_index else BLACK
        card_text = f"{i}: {card.name} (Energy: {card.energy_cost.value})"
        render_text(
            screen,
            card_text,
            card_list_x + scale(10),
            card_list_y + scale(10) + i * scale(30),
            color=color,
            font=SMALL_FONT,
        )

    # Render selected card on the right
    if 0 <= selected_index < len(full_deck):
        selected_card = full_deck[selected_index]
        render_card(
            screen,
            selected_card,
            SCREEN_WIDTH - CARD_WIDTH - scale(40),
            header_height + scale(20),
            True,
            assets,
            player.energy.value,
            player.max_energy.value,
            player.bonus_damage,
            player.strength,
        )

    instructions = "Use UP/DOWN arrows to navigate, ENTER to select, ESC to cancel"
    render_text(
        screen,
        instructions,
        scale(20),
        SCREEN_HEIGHT - scale(30),
        color=BLACK,
        font=SMALL_FONT,
    )
    pygame.display.flip()


def render_with_opacity(
    screen: pygame.Surface, image: pygame.Surface, x: int, y: int, opacity: int
):
    temp = pygame.Surface(image.get_size(), pygame.SRCALPHA)
    temp.blit(image, (0, 0))
    temp.fill((255, 255, 255, opacity), None, pygame.BLEND_RGBA_MULT)
    screen.blit(temp, (x, y))
