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
        frames_list = settings.FRAMES.get(self.texture, [])
        if frames_list:
            if len(frames_list) == 1:
                frame = frames_list[0]
            elif self.texture == "guard":
                guard_dirs = {"down": 0, "right": 5, "left": 5, "up": 10}
                frame = frames_list[guard_dirs.get(self.direction, 0)]
            elif self.texture == "gallagher":
                gallagher_dirs = {"down": 0, "right": 8, "left": 8, "up": 4}
                frame = frames_list[gallagher_dirs.get(self.direction, 0)]
            else:
                frame = frames_list[DIRECTIONS.get(self.direction, 0)]
            return pygame.Rect(round(self.x), round(self.y), frame.width, frame.height)
        return pygame.Rect(round(self.x), round(self.y), 16, 18)

    @rect.setter
    def rect(self, value: pygame.Rect) -> None:
        self.x = value.x
        self.y = value.y

    def render(self, surface: pygame.Surface, camera: Any = None) -> None:
        frames_list = settings.FRAMES[self.texture]
        texture = settings.TEXTURES[self.texture]

        if len(frames_list) == 1:
            frame = frames_list[0]
            sub = texture.subsurface(frame)
            image = pygame.transform.flip(sub, True, False) if self.direction == "left" else sub
            position = pygame.Rect(round(self.x), round(self.y), frame.width, frame.height)
            if camera is not None:
                position = camera.apply(position)
            surface.blit(image, position)
        elif self.texture == "guard":
            guard_dirs = {"down": 0, "right": 5, "left": 5, "up": 10}
            frame = frames_list[guard_dirs.get(self.direction, 0)]
            sub = texture.subsurface(frame)
            image = pygame.transform.flip(sub, True, False) if self.direction == "left" else sub
            position = pygame.Rect(round(self.x), round(self.y), frame.width, frame.height)
            if camera is not None:
                position = camera.apply(position)
            surface.blit(image, position)
        elif self.texture == "gallagher":
            gallagher_dirs = {"down": 0, "right": 8, "left": 8, "up": 4}
            frame = frames_list[gallagher_dirs.get(self.direction, 0)]
            sub = texture.subsurface(frame)
            image = pygame.transform.flip(sub, True, False) if self.direction == "left" else sub
            position = pygame.Rect(round(self.x), round(self.y), frame.width, frame.height)
            if camera is not None:
                position = camera.apply(position)
            surface.blit(image, position)
        else:
            frame = frames_list[DIRECTIONS.get(self.direction, 0)]
            position = pygame.Rect(round(self.x), round(self.y), frame.width, frame.height)
            if camera is not None:
                position = camera.apply(position)
            surface.blit(texture, position, frame)
            surface.blit(settings.TEXTURES[self.texture], position, frame)