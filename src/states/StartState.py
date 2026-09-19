from typing import Any

import pygame

from gale.state import BaseState

import settings


class StartState(BaseState):
    def __init__(self, state_machine: Any = None) -> None:
        super().__init__(state_machine)
        raw_logo = settings.TEXTURES.get("logo")
        if raw_logo is not None:
            # Preserva la relación de aspecto 2816x1536 en 480x270 virtual
            self.bg = pygame.transform.smoothscale(raw_logo, (495, settings.VIRTUAL_HEIGHT))
            self.bg_x = (settings.VIRTUAL_WIDTH - 495) // 2
        else:
            self.bg = None

    def render(self, surface: pygame.Surface) -> None:
        if self.bg is not None:
            surface.blit(self.bg, (self.bg_x, 0))
        else:
            surface.fill((18, 24, 30))

        # Placa inferior con el prompt de inicio
        prompt_text = "Presiona Enter para investigar"
        font = settings.FONTS["medium"]
        tw, th = font.size(prompt_text)

        pill_w = tw + 20
        pill_h = th + 6
        pill_x = (settings.VIRTUAL_WIDTH - pill_w) // 2
        pill_y = 238

        pill = pygame.Surface((pill_w, pill_h), pygame.SRCALPHA)
        pill.fill((10, 12, 16, 180))
        pygame.draw.rect(pill, (180, 145, 50, 160), pygame.Rect(0, 0, pill_w, pill_h), 1)
        surface.blit(pill, (pill_x, pill_y))

        txt = font.render(prompt_text, True, (240, 230, 200))
        surface.blit(txt, txt.get_rect(center=(settings.VIRTUAL_WIDTH // 2, pill_y + pill_h // 2)))

    def on_input(self, input_id: str, input_data: Any) -> None:
        if input_id in ("enter", "space") and getattr(input_data, "pressed", False):
            from src.states.PlayState import PlayState

            self.state_machine.pop()
            self.state_machine.push(PlayState(self.state_machine))
