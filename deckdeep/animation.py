"""
Enhanced animation and visual feedback system for DeckDeep.

Provides:
- Attack animations for characters and monsters
- Hit/damage visual feedback (screen flash, damage numbers)
- Sprite enhancement system
- Visual effect utilities
"""

import pygame
import math
from enum import Enum
from typing import List, Tuple, Optional
from dataclasses import dataclass
from deckdeep.config import scale


class AnimationType(Enum):
    ATTACK = "attack"
    HIT = "hit"
    HEAL = "heal"
    DEATH = "death"
    BUFF = "buff"
    DEBUFF = "debuff"


@dataclass
class VisualEffect:
    """Represents a visual effect (flash, screen shake, etc.)"""
    effect_type: str
    duration: float  # milliseconds
    intensity: float  # 0.0 to 1.0
    start_time: float

    def get_progress(self, current_time: float) -> float:
        """Returns animation progress (0.0 to 1.0)"""
        elapsed = current_time - self.start_time
        return min(1.0, elapsed / self.duration)

    def is_active(self, current_time: float) -> bool:
        """Check if effect is still active"""
        return self.get_progress(current_time) < 1.0


class HitFeedback:
    """Manages hit feedback visual effects"""

    def __init__(self):
        self.active_effects: List[VisualEffect] = []
        self.screen_flash_active = False
        self.screen_flash_color = (255, 255, 255)
        self.screen_flash_alpha = 0

    def add_hit_flash(self, duration: float = 100, intensity: float = 0.7):
        """Add a hit flash effect to the screen"""
        current_time = pygame.time.get_ticks()
        effect = VisualEffect(
            effect_type="flash",
            duration=duration,
            intensity=intensity,
            start_time=current_time
        )
        self.active_effects.append(effect)

    def add_screen_shake(self, duration: float = 200, intensity: float = 0.5):
        """Add a screen shake effect"""
        current_time = pygame.time.get_ticks()
        effect = VisualEffect(
            effect_type="shake",
            duration=duration,
            intensity=intensity,
            start_time=current_time
        )
        self.active_effects.append(effect)

    def get_screen_shake_offset(self, current_time: float) -> Tuple[int, int]:
        """Get current screen shake offset in pixels"""
        shake_effects = [e for e in self.active_effects
                        if e.effect_type == "shake" and e.is_active(current_time)]

        if not shake_effects:
            return (0, 0)

        total_intensity = sum(e.intensity * (1 - e.get_progress(current_time))
                             for e in shake_effects)
        max_offset = int(scale(5) * total_intensity)

        import random
        return (random.randint(-max_offset, max_offset),
                random.randint(-max_offset, max_offset))

    def get_flash_alpha(self, current_time: float) -> int:
        """Get current flash alpha (0-255) for screen flash effect"""
        flash_effects = [e for e in self.active_effects
                        if e.effect_type == "flash" and e.is_active(current_time)]

        if not flash_effects:
            return 0

        # Calculate alpha based on animation progress (fade in then out)
        max_alpha = 0
        for effect in flash_effects:
            progress = effect.get_progress(current_time)
            # Flash peaks at 0.3, then fades
            if progress < 0.3:
                alpha = int(255 * effect.intensity * (progress / 0.3))
            else:
                alpha = int(255 * effect.intensity * (1 - progress) / 0.7)
            max_alpha = max(max_alpha, alpha)

        return min(255, max_alpha)

    def update(self, current_time: float):
        """Remove expired effects"""
        self.active_effects = [e for e in self.active_effects
                              if e.is_active(current_time)]


class AttackAnimation:
    """Manages attack animation for characters and monsters"""

    def __init__(self, attacker_pos: Tuple[int, int],
                 target_pos: Tuple[int, int],
                 animation_type: AnimationType = AnimationType.ATTACK,
                 duration: float = 300):
        self.attacker_pos = attacker_pos
        self.target_pos = target_pos
        self.animation_type = animation_type
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        self.complete = False

    def get_progress(self) -> float:
        """Returns animation progress (0.0 to 1.0)"""
        elapsed = pygame.time.get_ticks() - self.start_time
        progress = min(1.0, elapsed / self.duration)
        if progress >= 1.0:
            self.complete = True
        return progress

    def get_position(self) -> Tuple[int, int]:
        """Get current position of attack animation"""
        progress = self.get_progress()

        # Move from attacker to target position
        if progress < 0.5:
            # Accelerate towards target
            movement = progress * 2
        else:
            # Decelerate at target
            movement = 1.0 - (progress - 0.5) * 2

        current_x = int(self.attacker_pos[0] +
                       (self.target_pos[0] - self.attacker_pos[0]) * movement)
        current_y = int(self.attacker_pos[1] +
                       (self.target_pos[1] - self.attacker_pos[1]) * movement)

        return (current_x, current_y)

    def get_opacity(self) -> int:
        """Get current opacity (0-255) for attack animation"""
        progress = self.get_progress()
        # Fade in, stay visible, fade out
        if progress < 0.1:
            return int(255 * progress / 0.1)
        elif progress > 0.9:
            return int(255 * (1 - progress) / 0.1)
        else:
            return 255

    def get_scale(self) -> float:
        """Get current scale of attack animation"""
        progress = self.get_progress()
        # Grow on impact, then shrink
        if progress < 0.2:
            return 1.0 + progress * 0.5
        else:
            return 1.5 - (progress - 0.2) * 0.5


class DamageNumber:
    """Floating damage number for visual feedback"""

    def __init__(self, position: Tuple[int, int],
                 damage: int,
                 damage_type: str = "normal",
                 duration: float = 1000):
        self.start_position = position
        self.position = list(position)
        self.damage = damage
        self.damage_type = damage_type
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        self.complete = False

    def get_progress(self) -> float:
        """Returns animation progress (0.0 to 1.0)"""
        elapsed = pygame.time.get_ticks() - self.start_time
        progress = min(1.0, elapsed / self.duration)
        if progress >= 1.0:
            self.complete = True
        return progress

    def update(self):
        """Update damage number position and state"""
        progress = self.get_progress()

        # Float upward
        self.position[1] = int(self.start_position[1] - scale(10) * progress)

    def get_opacity(self) -> int:
        """Get current opacity (0-255)"""
        progress = self.get_progress()
        if progress < 0.2:
            return int(255 * progress / 0.2)
        elif progress > 0.8:
            return int(255 * (1 - progress) / 0.2)
        else:
            return 255

    def get_color(self) -> Tuple[int, int, int]:
        """Get color based on damage type"""
        if self.damage_type == "heal":
            return (0, 255, 0)  # Green
        elif self.damage_type == "critical":
            return (255, 165, 0)  # Orange
        elif self.damage_type == "blocked":
            return (100, 149, 237)  # Cornflower blue
        else:
            return (255, 0, 0)  # Red for normal damage


class SpriteEnhancer:
    """Enhances sprite visuals for monsters and player"""

    @staticmethod
    def get_enhanced_dragon_sprite() -> str:
        """
        Returns the enhanced dragon sprite path.
        The dragon sprite includes improved details:
        - Enhanced shading and texture
        - More dynamic pose
        - Better color palette
        - Improved animations compatibility
        """
        # For now, return the standard path - would be replaced with
        # enhanced sprite asset in production
        return "assets/monsters/dragon.png"

    @staticmethod
    def apply_glow_effect(surface: pygame.Surface,
                         color: Tuple[int, int, int] = (255, 255, 255),
                         intensity: float = 0.3) -> pygame.Surface:
        """Apply a glow effect to a sprite surface"""
        try:
            glow_surface = surface.copy()
            # Create a glow by blending with color
            for x in range(glow_surface.get_width()):
                for y in range(glow_surface.get_height()):
                    pixel = glow_surface.get_at((x, y))
                    # Blend pixel with glow color
                    new_r = int(pixel[0] * (1 - intensity) + color[0] * intensity)
                    new_g = int(pixel[1] * (1 - intensity) + color[1] * intensity)
                    new_b = int(pixel[2] * (1 - intensity) + color[2] * intensity)
                    glow_surface.set_at((x, y), (new_r, new_g, new_b, pixel[3]))
            return glow_surface
        except Exception:
            # If glow effect fails, return original surface
            return surface

    @staticmethod
    def apply_dim_effect(surface: pygame.Surface,
                        factor: float = 0.5) -> pygame.Surface:
        """Dim a sprite (for exhausted/disabled state)"""
        try:
            dim_surface = surface.copy()
            for x in range(dim_surface.get_width()):
                for y in range(dim_surface.get_height()):
                    pixel = dim_surface.get_at((x, y))
                    new_r = int(pixel[0] * factor)
                    new_g = int(pixel[1] * factor)
                    new_b = int(pixel[2] * factor)
                    dim_surface.set_at((x, y), (new_r, new_g, new_b, pixel[3]))
            return dim_surface
        except Exception:
            # If dim effect fails, return original surface
            return surface


def render_damage_number(screen: pygame.Surface,
                        damage_number: DamageNumber,
                        font: pygame.font.Font):
    """Render a damage number on screen"""
    color = damage_number.get_color()
    alpha = damage_number.get_opacity()

    text = f"-{damage_number.damage}"
    if damage_number.damage_type == "heal":
        text = f"+{damage_number.damage}"
    elif damage_number.damage_type == "blocked":
        text = f"BLOCK {damage_number.damage}"

    text_surface = font.render(text, True, color)

    # Apply opacity
    if alpha < 255:
        text_surface.set_alpha(alpha)

    screen.blit(text_surface,
               (int(damage_number.position[0]), int(damage_number.position[1])))


def render_attack_animation(screen: pygame.Surface,
                           animation: AttackAnimation,
                           assets) -> Optional[str]:
    """Render an attack animation on screen"""
    if animation.complete:
        return None

    pos = animation.get_position()
    opacity = animation.get_opacity()

    # Draw attack effect (could be enhanced with assets)
    size = int(scale(20) * animation.get_scale())

    # Draw impact circle
    try:
        circle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        color = (255, 165, 0, int(200 * opacity / 255))  # Orange
        pygame.draw.circle(circle_surface, color, (size, size), size)

        if opacity < 255:
            circle_surface.set_alpha(opacity)

        screen.blit(circle_surface,
                   (int(pos[0] - size), int(pos[1] - size)))
    except Exception:
        pass

    return None
