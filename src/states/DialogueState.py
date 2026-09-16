"""
P.I. Gallagher: The Missing Art

DialogueState — Noir 1932 styled dialogue interface.
Supports multi-page sequences, speaker plaques, word wrapping,
and callback execution upon dialogue completion.
"""

from typing import Any, Callable, List, Optional, Union

import pygame

from gale.state import BaseState
from gale.text import render_text

import settings


class DialogueState(BaseState):
    # Palette Noir 1932
    COLOR_BG = (28, 24, 22)
    COLOR_PAPER = (215, 198, 168)
    COLOR_BORDER = (175, 140, 65)
    COLOR_BORDER_DARK = (120, 95, 45)
    COLOR_INK = (25, 22, 20)
    COLOR_TEXT_LIGHT = (225, 220, 205)
    COLOR_SPEAKER_BG = (45, 38, 32)
    COLOR_MUTED = (145, 135, 120)

    def enter(
        self,
        text: Union[str, List[str]],
        speaker: str = "",
        on_finish: Optional[Callable[[], None]] = None,
    ) -> None:
        if isinstance(text, str):
            self.pages = [text]
        else:
            self.pages = list(text) if text else ["..."]

        self.speaker = speaker
        self.on_finish = on_finish
        self.page_index = 0

    def on_input(self, input_id: str, input_data: Any) -> None:
        if not input_data.pressed:
            return

        if input_id in ("interact", "enter", "confirm"):
            if self.page_index < len(self.pages) - 1:
                self.page_index += 1
            else:
                if self.on_finish is not None:
                    callback = self.on_finish
                    self.on_finish = None
                    callback()
                self.state_machine.pop()

    def _wrap_text(self, text: str, max_width: int) -> List[str]:
        words = text.split()
        lines = []
        current_line = ""
        font = settings.FONTS["small"]

        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)
        return lines

    def render(self, surface: pygame.Surface) -> None:
        # Subtle dark veil over the world
        overlay = pygame.Surface(
            (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 80))
        surface.blit(overlay, (0, 0))

        # Main dialogue box (bottom of the screen)
        bx = 16
        by = settings.VIRTUAL_HEIGHT - 82
        bw = settings.VIRTUAL_WIDTH - 32
        bh = 72

        box_rect = pygame.Rect(bx, by, bw, bh)

        # Background and border
        pygame.draw.rect(surface, self.COLOR_BG, box_rect, border_radius=4)
        pygame.draw.rect(surface, self.COLOR_BORDER, box_rect, 2, border_radius=4)
        pygame.draw.rect(
            surface, self.COLOR_BORDER_DARK, box_rect.inflate(-4, -4), 1, border_radius=3
        )

        # Speaker name plaque (if provided)
        if self.speaker:
            name_text = f" {self.speaker} "
            nw, nh = settings.FONTS["small"].size(name_text)
            name_rect = pygame.Rect(bx + 14, by - 12, nw + 12, nh + 4)
            pygame.draw.rect(surface, self.COLOR_SPEAKER_BG, name_rect, border_radius=3)
            pygame.draw.rect(surface, self.COLOR_BORDER, name_rect, 1, border_radius=3)
            render_text(
                surface,
                self.speaker,
                settings.FONTS["small"],
                name_rect.centerx,
                name_rect.y + 2,
                self.COLOR_BORDER,
                center=True,
            )

        # Current page text (word wrapped)
        current_text = self.pages[self.page_index]
        wrapped_lines = self._wrap_text(current_text, bw - 28)

        text_y = by + 12
        for line in wrapped_lines[:3]:
            render_text(
                surface,
                line,
                settings.FONTS["small"],
                bx + 14,
                text_y,
                self.COLOR_TEXT_LIGHT,
            )
            text_y += 16

        # Navigation hint / page indicator
        total_pages = len(self.pages)
        if total_pages > 1:
            page_hint = f"[{self.page_index + 1}/{total_pages}]  ESPACIO / ENTER >>"
        else:
            page_hint = "ESPACIO / ENTER para cerrar"

        render_text(
            surface,
            page_hint,
            settings.FONTS["small"],
            box_rect.right - 14,
            box_rect.bottom - 16,
            self.COLOR_MUTED,
            center=False,
        )
