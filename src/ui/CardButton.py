"""
P.I. Gallagher: The Missing Art

CorkboardState — Central investigative corkboard built entirely on gale.ui.
Features 2D grid navigation across clue cards, seamless focus transition to bottom
action buttons, mouse click and motion support, a dedicated full-screen Card Details
overlay, and modal dialogs for deductions and Lauren's hints.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple

import pygame

from gale.text import render_text
from gale.ui import Button, Theme

import settings
from src.ui.theme import (
    COLOR_ACCENT_RED,
    COLOR_BRASS,
    COLOR_BRASS_LIGHT,
    COLOR_INK,
    COLOR_MUTED,
    COLOR_PAPER,
    COLOR_PAPER_SELECTED,
    COLOR_PAPER_THREADED,
    COLOR_SUCCESS,
    NOIR_BUTTON_THEME,
    NOIR_CARD_THEME,
    NOIR_CORK_THEME,
    NOIR_DIALOGUE_THEME,
    NOIR_SIDEBAR_THEME,
)

class CardButton(Button):
    """
    gale.ui.Button representing an individual clue card on the corkboard.
    Displays ID, Title, primary keywords, pin indicator, and clear focus styling.
    """

    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        card_data: Dict[str, Any],
        on_toggle: Callable[[], None],
        theme: Optional[Theme] = None,
    ) -> None:
        super().__init__(x, y, width, height, text="", on_click=on_toggle, theme=theme)
        self.card_data = card_data
        self.is_threaded: bool = False

    @property
    def pin_pos(self) -> Tuple[int, int]:
        return int(self.x + self.width // 2), int(self.y + 3)

    def render(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return

        # Background color
        if self.is_threaded:
            bg_color = COLOR_PAPER_THREADED
        elif self.focused or self.hovered:
            bg_color = COLOR_PAPER_SELECTED
        else:
            bg_color = COLOR_PAPER

        pygame.draw.rect(surface, bg_color, self.rect, border_radius=3)

        # Border outline: strong visual distinction for focused card
        if self.focused:
            pygame.draw.rect(surface, COLOR_BRASS_LIGHT, self.rect, 2, border_radius=3)
        elif self.is_threaded:
            pygame.draw.rect(surface, COLOR_ACCENT_RED, self.rect, 2, border_radius=3)
        elif self.hovered:
            pygame.draw.rect(surface, COLOR_BRASS, self.rect, 1, border_radius=3)
        else:
            pygame.draw.rect(surface, pygame.Color(140, 130, 115), self.rect, 1, border_radius=3)

        # Thumbtack pin at top center
        px, py = self.pin_pos
        pin_color = COLOR_ACCENT_RED if self.is_threaded else pygame.Color(230, 175, 45)
        pygame.draw.circle(surface, pin_color, (px, py), 3)
        if self.is_threaded:
            pygame.draw.circle(surface, pygame.Color(255, 140, 140), (px, py), 1)

        # Card Title with cursor indicator when focused
        cid = self.card_data["id"]
        title = self.card_data["titulo"]
        title_prefix = "> " if self.focused else ""
        render_text(
            surface,
            f"{title_prefix}[{cid}] {title}",
            settings.FONTS["small"],
            self.x + 4,
            self.y + 6,
            COLOR_INK,
        )

        # Highlighted Keywords
        kw_list = self.card_data.get("claves", [])
        kw_str = kw_list[0] if kw_list else ""
        if len(kw_list) > 1:
            kw_str += f", {kw_list[1]}"

        render_text(
            surface,
            kw_str,
            settings.FONTS["small"],
            self.x + 4,
            self.y + 20,
            COLOR_ACCENT_RED,
        )

        # Right-aligned details badge
        render_text(
            surface,
            "[D: Ver]",
            settings.FONTS["small"],
            self.rect.right - 44,
            self.y + 20,
            COLOR_MUTED,
        )