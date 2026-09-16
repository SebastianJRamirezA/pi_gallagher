from typing import Any

import pygame

import settings


DIRECTIONS = {
    "up": 1,
    "right": 4,
    "down": 7,
    "left": 10,
}


class Actor:
    def __init__(self, x: float, y: float, texture: str, name: str, direction: str = "down") -> None:
        self.x = x
        self.y = y
        self.texture = texture
        self.name = name
        self.direction = direction
        self.width = 14
        self.height = 18

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(round(self.x + 1), round(self.y - 2), self.width, self.height)

    def render(self, surface: pygame.Surface, camera: Any = None) -> None:
        frame = settings.FRAMES[self.texture][DIRECTIONS[self.direction]]
        position = pygame.Rect(round(self.x), round(self.y), self.width, self.height)
        if camera is not None:
            position = camera.apply(position)
        surface.blit(settings.TEXTURES[self.texture], position, frame)


class Player(Actor):
    SPEED = 92.0

    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, "player", "Tim Gallagher")
        self.held = {"move_left": False, "move_right": False, "move_up": False, "move_down": False}

    def on_input(self, input_id: str, input_data: Any) -> None:
        if input_id in self.held:
            self.held[input_id] = input_data.pressed or not input_data.released

    def move(self, dx: float, dy: float) -> None:
        if dx:
            self.direction = "right" if dx > 0 else "left"
        elif dy:
            self.direction = "down" if dy > 0 else "up"


class NPC(Actor):
    LINES = (
        "I saw someone carrying a painting toward the back rooms.",
        "The gallery's night guard has been acting nervous.",
        "Ask around. Someone here knows where the masterpiece went.",
    )

    def __init__(self, x: float, y: float, name: str) -> None:
        super().__init__(x, y, "npc", name)

    def dialogue(self) -> str:
        import random

        return f"{self.name}: {random.choice(self.LINES)}"
