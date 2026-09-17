from typing import Any

import pygame
from gale.state import BaseState

import settings


class DialogueState(BaseState):
    def enter(self, text: str) -> None:
        self.text = text

    def on_input(self, input_id: str, input_data: Any) -> None:
        if input_id in ("interact", "enter") and input_data.pressed:
            self.state_machine.pop()

    def render(self, surface: pygame.Surface) -> None:
        box = pygame.Rect(12, settings.VIRTUAL_HEIGHT - 76, settings.VIRTUAL_WIDTH - 24, 60)
        pygame.draw.rect(surface, (24, 28, 34), box)
        pygame.draw.rect(surface, (230, 220, 180), box, 2)
        text = settings.FONTS["small"].render(self.text, True, (255, 255, 255))
        surface.blit(text, (box.x + 10, box.y + 12))
        hint = settings.FONTS["small"].render("Enter / Space to close", True, (170, 180, 180))
        surface.blit(hint, (box.x + 10, box.bottom - 20))
