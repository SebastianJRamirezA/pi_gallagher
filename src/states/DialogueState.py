"""
P.I. Gallagher: The Missing Art

DialogueState — Refactored using gale.ui (Window, TextBox, Label, Container, UIManager).
Renders dialogue in a 1932 Noir aesthetic with pagination, speaker plaque, and click/key advancing.
"""

from typing import Any, Callable, List, Optional, Union

import pygame

from gale.input_handler import KeyboardData
from gale.state import BaseState
from gale.ui import Container, Label, TextBox, Theme, UIManager, Window

import settings
from src.ui.theme import NOIR_DIALOGUE_THEME


class DialogueTextBox(TextBox):
    """
    Subclass of gale.ui.TextBox that accepts multiple pages/paragraphs
    and automatically partitions them according to lines_per_page.
    """

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
        # Inner theme with no extra border so it blends cleanly into the Window
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

    def _paginate(self, text: str) -> List[List[str]]:
        if not hasattr(self, "raw_pages"):
            return [[]]

        font = self._font if self._font is not None else self.theme.font
        all_pages: List[List[str]] = []

        for p in self.raw_pages:
            wrapped = self._wrap(p, font)
            for i in range(0, len(wrapped), self.lines_per_page):
                all_pages.append(wrapped[i : i + self.lines_per_page])

        return all_pages or [[]]


class DialogueState(BaseState):
    def enter(
        self,
        text: Union[str, List[str]],
        speaker: str = "",
        on_finish: Optional[Callable[[], None]] = None,
    ) -> None:
        self.speaker = speaker or "P.I. Gallagher"
        self.on_finish = on_finish

        # Root container for gale.ui
        self.root = Container(0, 0, settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT)

        # Dialogue Window docked at bottom of screen
        win_x = 16
        win_y = settings.VIRTUAL_HEIGHT - 82
        win_w = settings.VIRTUAL_WIDTH - 32
        win_h = 72

        self.window = Window(
            win_x,
            win_y,
            win_w,
            win_h,
            title=self.speaker,
            closable=False,
            theme=NOIR_DIALOGUE_THEME,
        )

        # Dialogue text box inside the window
        tb_x = win_x + 10
        tb_y = win_y + 24
        tb_w = win_w - 20
        tb_h = 44

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

        # Footer page indicator / navigation hint
        self.hint_label = Label(
            win_x + win_w - 120,
            win_y + win_h - 14,
            text="",
            font=settings.FONTS["small"],
            color=pygame.Color(160, 150, 135),
            theme=NOIR_DIALOGUE_THEME,
        )
        self.window.add_child(self.hint_label)
        self._update_hint_text()

        self.root.add_child(self.window)

        # UIManager to route mouse clicks and keyboard actions
        self.ui = UIManager(
            self.root,
            virtual_width=settings.VIRTUAL_WIDTH,
            window_width=settings.WINDOW_WIDTH,
            virtual_height=settings.VIRTUAL_HEIGHT,
            window_height=settings.WINDOW_HEIGHT,
            confirm_action="confirm",
        )

    def _update_hint_text(self) -> None:
        total = self.textbox.page_count
        current = self.textbox.page_index + 1
        if total > 1:
            self.hint_label.set_text(f"[{current}/{total}]  ESPACIO >>")
        else:
            self.hint_label.set_text("ESPACIO para cerrar")

    def _close_dialogue(self) -> None:
        if self.on_finish is not None:
            cb = self.on_finish
            self.on_finish = None
            cb()
        self.state_machine.pop()

    def update(self, dt: float) -> None:
        self.ui.update(dt)
        self._update_hint_text()

    def on_input(self, input_id: str, input_data: Any) -> None:
        if isinstance(input_data, KeyboardData) and not input_data.pressed:
            return

        if input_id in ("interact", "enter", "confirm"):
            self.textbox.advance()
            return

        self.ui.on_input(input_id, input_data)

    def render(self, surface: pygame.Surface) -> None:
        # Subtle dark veil over the world
        overlay = pygame.Surface(
            (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 85))
        surface.blit(overlay, (0, 0))

        # Render gale.ui widget tree
        self.ui.render(surface)
