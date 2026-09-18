"""
P.I. Gallagher: The Missing Art

DialogueState — Refactored using gale.ui (Window, TextBox, Label, Container, UIManager).
Renders dialogue in a 1932 Noir aesthetic with working typewriter animation, 
pagination, speaker plaque, and back/forth navigation.
"""

from typing import Any, Callable, List, Optional, Union

import pygame

from gale.input_handler import KeyboardData
from gale.state import BaseState
from gale.ui import Container, Label, TextBox, Theme, UIManager, Window

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


class DialogueState(BaseState):
    def enter(
        self,
        text: Union[str, List[str]],
        speaker: str = "",
        on_finish: Optional[Callable[[], None]] = None,
    ) -> None:
        self.speaker = speaker or "P.I. Gallagher"
        self.on_finish = on_finish

        self.root = Container(0, 0, settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT)

        win_x = 16
        win_y = settings.VIRTUAL_HEIGHT - 96
        win_w = settings.VIRTUAL_WIDTH - 32
        win_h = 88

        self.window = Window(
            win_x,
            win_y,
            win_w,
            win_h,
            title="",
            closable=False,
            theme=NOIR_DIALOGUE_THEME,
        )

        self.speaker_label = Label(
            win_x + 12,
            win_y + 8,
            text=self.speaker.upper(),
            font=settings.FONTS.get("bold", settings.FONTS["medium"]),
            color=pygame.Color(212, 175, 55),
            theme=NOIR_DIALOGUE_THEME,
        )
        self.window.add_child(self.speaker_label)

        tb_x = win_x + 12
        tb_y = win_y + 26
        tb_w = win_w - 24
        tb_h = 42

        self.textbox = DialogueTextBox(
            tb_x,
            tb_y,
            tb_w,
            tb_h,
            pages=text,
            lines_per_page=3,
            on_close=self._close_dialogue,
            theme=NOIR_DIALOGUE_THEME,
        )
        self.window.add_child(self.textbox)

        self.hint_label = Label(
            win_x + 12,
            win_y + win_h - 16,
            text="",
            font=settings.FONTS["small"],
            color=pygame.Color(160, 150, 135),
            theme=NOIR_DIALOGUE_THEME,
        )
        self.window.add_child(self.hint_label)
        self._update_hint_text()

        self.root.add_child(self.window)

        self.ui = UIManager(
            self.root,
            virtual_width=settings.VIRTUAL_WIDTH,
            window_width=settings.WINDOW_WIDTH,
            virtual_height=settings.VIRTUAL_HEIGHT,
            window_height=settings.WINDOW_HEIGHT,
            confirm_action="space",
        )

    def _update_hint_text(self) -> None:
        total = self.textbox.page_count
        current = self.textbox.page_index + 1

        nav_hints = []
        if current > 1:
            nav_hints.append("◄ [IZQ] Atrás")
        if current < total:
            nav_hints.append("[ESPACIO] Avanzar ►")
        else:
            nav_hints.append("[ESPACIO] Cerrar")

        hint_str = f"Pág. {current}/{total}  |  " + "  ".join(nav_hints)
        self.hint_label.set_text(hint_str)

    def _close_dialogue(self) -> None:
        if self.on_finish is not None:
            cb = self.on_finish
            self.on_finish = None
            cb()
        self.state_machine.pop()

    def update(self, dt: float) -> None:
        # Crucial: Explicitly tick the textbox animation every frame
        self.textbox.update(dt)
        self.ui.update(dt)
        self._update_hint_text()

    def on_input(self, input_id: str, input_data: Any) -> None:
        if isinstance(input_data, KeyboardData) and not input_data.pressed:
            return

        if input_id in ("space", "enter", "move_right"):
            self.textbox.advance()
            return
        elif input_id == "move_left":
            self.textbox.regress()
            return

        self.ui.on_input(input_id, input_data)

    def render(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface(
            (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 85))
        surface.blit(overlay, (0, 0))

        self.ui.render(surface)