"""
P.I. Gallagher: The Missing Art

PauseMenuState — Refactored using gale.ui (Window, ListView, Container, UIManager).
"""

from typing import Any

import pygame
from gale.input_handler import KeyboardData
from gale.state import BaseState
from gale.ui import Container, ListView, UIManager, Window

import settings
from src.ui.theme import NOIR_MENU_THEME


class PauseMenuState(BaseState):
    def enter(self) -> None:
        def on_continue():
            self.state_machine.pop()

        def on_quit():
            self.state_machine.clear()
            from src.states.StartState import StartState

            self.state_machine.push(StartState(self.state_machine))

        self.root = Container(0, 0, settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT)

        menu_w = 160
        menu_h = 100
        menu_x = settings.VIRTUAL_WIDTH // 2 - menu_w // 2
        menu_y = settings.VIRTUAL_HEIGHT // 2 - menu_h // 2

        self.window = Window(
            menu_x,
            menu_y,
            menu_w,
            menu_h,
            title="PAUSA",
            closable=False,
            theme=NOIR_MENU_THEME,
        )

        self.list_view = ListView(
            menu_x + 12,
            menu_y + 32,
            menu_w - 24,
            54,
            items=[
                ("Continuar", on_continue),
                ("Salir al Menú", on_quit),
            ],
            theme=NOIR_MENU_THEME,
        )
        self.window.add_child(self.list_view)
        self.root.add_child(self.window)

        self.ui = UIManager(
            self.root,
            virtual_width=settings.VIRTUAL_WIDTH,
            window_width=settings.WINDOW_WIDTH,
            virtual_height=settings.VIRTUAL_HEIGHT,
            window_height=settings.WINDOW_HEIGHT,
            confirm_action="enter",
            navigate_actions={"move_up": (0, -1), "move_down": (0, 1)},
        )

    def update(self, dt: float) -> None:
        self.ui.update(dt)

    def on_input(self, input_id: str, input_data: Any) -> None:
        if isinstance(input_data, KeyboardData) and not input_data.pressed:
            return

        if input_id in ("pause", "quit"):
            self.state_machine.pop()
            return

        if input_id == "interact":
            # Space can also trigger confirm
            self.root.on_confirm()
            return

        self.ui.on_input(input_id, input_data)

    def render(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        self.ui.render(surface)
