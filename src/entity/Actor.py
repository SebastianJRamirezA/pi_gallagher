"""
P.I. Gallagher: The Missing Art

Actor entities: Actor (base), Player (state-machine driven), NPC.
"""

from typing import Any

import pygame

import settings


# Direction → frame index for NPC placeholder sprites (3 cols x 4 rows).
DIRECTIONS = {
    "up": 1,
    "right": 4,
    "down": 7,
    "left": 10,
}

class Actor:
    """Base actor with position, direction, and simple sprite rendering."""

    def __init__(
        self, x: float, y: float, texture: str, name: str, direction: str = "down"
    ) -> None:
        self.x = x
        self.y = y
        self.texture = texture
        self.name = name
        self.direction = direction
        self.width = 14
        self.height = 14

    @property
    def rect(self) -> pygame.Rect:
        # Full sprite bounds (16x18) anchored at the sprite origin — matches what is rendered.
        return pygame.Rect(round(self.x), round(self.y), 16, 18)

    @rect.setter
    def rect(self, value: pygame.Rect) -> None:
        self.x = value.x
        self.y = value.y

    def render(self, surface: pygame.Surface, camera: Any = None) -> None:
        frame = settings.FRAMES[self.texture][DIRECTIONS[self.direction]]
        position = pygame.Rect(round(self.x), round(self.y), frame.width, frame.height)
        if camera is not None:
            position = camera.apply(position)
        surface.blit(settings.TEXTURES[self.texture], position, frame)
        # Draw collision box for debugging
        if camera is not None:
            pygame.draw.rect(surface, (255, 0, 0), camera.apply(self.rect), 1)