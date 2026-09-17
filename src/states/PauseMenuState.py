from typing import Any

import pygame
from gale.state import BaseState

import settings


class PauseMenuState(BaseState):
    def enter(self) -> None:
        self.selected = 0
        self.items = ("Continue", "Quit")

    def on_input(self, input_id: str, input_data: Any) -> None:
        if not input_data.pressed:
            return
        if input_id in ("pause", "quit"):
            self.state_machine.pop()
        elif input_id == "move_up":
            self.selected = (self.selected - 1) % len(self.items)
        elif input_id == "move_down":
            self.selected = (self.selected + 1) % len(self.items)
        elif input_id == "enter":
            if self.selected == 0:
                self.state_machine.pop()
            else:
                self.state_machine.clear()
                self.state_machine.push(__import__("src.states.StartState", fromlist=["StartState"]).StartState(self.state_machine))

    def render(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        surface.blit(overlay, (0, 0))
        panel = pygame.Rect(settings.VIRTUAL_WIDTH / 2 - 78, settings.VIRTUAL_HEIGHT / 2 - 54, 156, 108)
        pygame.draw.rect(surface, (32, 36, 42), panel)
        pygame.draw.rect(surface, (230, 220, 180), panel, 2)
        title = settings.FONTS["medium"].render("PAUSED", True, (235, 220, 174))
        surface.blit(title, title.get_rect(center=(panel.centerx, panel.y + 24)))
        for index, item in enumerate(self.items):
            color = (255, 255, 255) if index == self.selected else (150, 160, 165)
            text = settings.FONTS["small"].render(("> " if index == self.selected else "  ") + item, True, color)
            surface.blit(text, (panel.x + 34, panel.y + 52 + index * 20))
