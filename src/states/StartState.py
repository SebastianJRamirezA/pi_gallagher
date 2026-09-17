from typing import Any

import pygame

from gale.state import BaseState

import settings


class StartState(BaseState):
    def render(self, surface: pygame.Surface) -> None:
        surface.fill((18, 24, 30))
        title = settings.FONTS["large"].render("P.I. GALLAGHER", True, (235, 220, 174))
        subtitle = settings.FONTS["large"].render("THE MISSING ART", True, (180, 190, 190))
        prompt = settings.FONTS["medium"].render("Press Enter to investigate", True, (235, 235, 235))
        surface.blit(title, title.get_rect(center=(settings.VIRTUAL_WIDTH / 2, 116)))
        surface.blit(subtitle, subtitle.get_rect(center=(settings.VIRTUAL_WIDTH / 2, 150)))
        surface.blit(prompt, prompt.get_rect(center=(settings.VIRTUAL_WIDTH / 2, 236)))

    def on_input(self, input_id: str, input_data: Any) -> None:
        if input_id in ("enter", "space") and input_data.pressed:
            from src.states.PlayState import PlayState

            self.state_machine.pop()
            self.state_machine.push(PlayState(self.state_machine))
