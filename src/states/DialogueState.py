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
from gale.ui import Container, Label, UIManager, Window

import settings
from src.ui import DialogueTextBox
from src.ui.theme import NOIR_DIALOGUE_THEME

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
        self.state_machine.pop()
        if self.on_finish is not None:
            cb = self.on_finish
            self.on_finish = None
            cb()

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