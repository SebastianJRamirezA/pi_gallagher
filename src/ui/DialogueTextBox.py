from typing import Callable, List, Optional, Union

import pygame

from gale.ui import TextBox, Theme

import settings
from src.text_utils import TypewriterEffect, wrap_text
from src.ui.theme import NOIR_DIALOGUE_THEME


class DialogueTextBox(TextBox):
    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        pages: Union[str, List[str]],
        lines_per_page: int = 3,
        on_close: Optional[Callable[[], None]] = None,
        theme: Optional[Theme] = None,
    ) -> None:
        self.raw_pages = [pages] if isinstance(pages, str) else list(pages)
        self.typewriter = TypewriterEffect(char_speed=0.025)

        inner_theme = Theme(
            font=theme.font if theme else None,
            text_color=theme.text_color if theme else pygame.Color(235, 228, 215),
            background_color=theme.background_color if theme else pygame.Color(28, 24, 22),
            border_color=theme.background_color if theme else pygame.Color(28, 24, 22),
            border_width=0,
            padding=2,
        )

        super().__init__(
            x,
            y,
            width,
            height,
            text="",
            lines_per_page=lines_per_page,
            on_close=on_close,
            theme=inner_theme,
        )

        self._load_current_page_typewriter()

    def _get_pages(self) -> List[List[str]]:
        if hasattr(self, "pages"):
            return self.pages
        elif hasattr(self, "_pages"):
            return self._pages
        return [[]]

    def _load_current_page_typewriter(self) -> None:
        pages = self._get_pages()
        if pages and self.page_index < len(pages):
            current_page_lines = pages[self.page_index]
            self.typewriter.set_text("\n".join(current_page_lines))

    def update(self, dt: float) -> None:
        """Advances typewriter effect on each game tick."""
        self.typewriter.update(dt)

    def advance(self) -> None:
        if not self.typewriter.finished:
            self.typewriter.complete()
            return

        if self.page_index < self.page_count - 1:
            self.page_index += 1
            self._load_current_page_typewriter()
        else:
            if self.on_close is not None:
                self.on_close()

    def regress(self) -> None:
        if self.page_index > 0:
            self.page_index -= 1
            self._load_current_page_typewriter()
            self.typewriter.complete()

    def render(self, surface: pygame.Surface) -> None:
        """Draws background surface and active typewriter text overlay."""
        # 1. Base widget background
        if hasattr(self, "surface") and self.surface:
            surface.blit(self.surface, self.rect)

        # 2. Render typed characters dynamically onto widget
        font = self._font if getattr(self, "_font", None) else self.theme.font
        visible_lines = self.typewriter.visible_text.split("\n")
        
        padding = getattr(self.theme, "padding", 2)
        text_color = getattr(self.theme, "text_color", (235, 228, 215))
        line_spacing = font.get_linesize()

        y_offset = self.rect.y + padding
        x_offset = self.rect.x + padding

        for line in visible_lines:
            if line:
                line_surface = font.render(line, True, text_color)
                surface.blit(line_surface, (x_offset, y_offset))
            y_offset += line_spacing

    def _paginate(self, text: str) -> List[List[str]]:
        if not hasattr(self, "raw_pages"):
            return [[]]

        font = self._font if self._font is not None else self.theme.font
        all_lines: List[str] = []
        max_w = self.rect.width - (self.theme.padding * 2)

        for p in self.raw_pages:
            wrapped = wrap_text(font, p, max_w)
            all_lines.extend(wrapped)

        if not all_lines:
            return [[]]

        raw_chunks = [
            all_lines[i : i + self.lines_per_page]
            for i in range(0, len(all_lines), self.lines_per_page)
        ]

        return self._balance_pages(raw_chunks)

    def _balance_pages(self, pages: List[List[str]]) -> List[List[str]]:
        if len(pages) > 1 and len(pages[-1]) == 1 and len(pages[-2]) > 1:
            borrowed_line = pages[-2].pop()
            pages[-1].insert(0, borrowed_line)
        return pages
