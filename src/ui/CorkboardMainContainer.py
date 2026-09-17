"""
P.I. Gallagher: The Missing Art

CorkboardState — Central investigative corkboard built entirely on gale.ui.
Features 2D grid navigation across clue cards, seamless focus transition to bottom
action buttons, mouse click and motion support, a dedicated full-screen Card Details
overlay, and modal dialogs for deductions and Lauren's hints.
"""

from typing import Tuple

import pygame

from gale.input_handler import MouseClickData
from gale.ui import Container
from gale.ui.widget import Direction

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

from src.ui import ActionBarContainer, CardGridContainer

class CorkboardMainContainer(Container):
    """
    Top-level UI Container coordinating the CardGridContainer and ActionBarContainer.
    Dispatches 2D arrow navigation seamlessly between the grid and bottom buttons.
    """

    def __init__(
        self,
        card_grid: CardGridContainer,
        action_bar: ActionBarContainer,
        **kwargs,
    ) -> None:
        super().__init__(0, 0, settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT, **kwargs)
        self.card_grid = card_grid
        self.action_bar = action_bar

    def on_navigate(self, direction: Direction) -> bool:
        _, dy = direction

        if self.action_bar.focused or any(b.focused for b in self.action_bar.children):
            if self.action_bar.on_navigate(direction):
                return True
            if dy < 0:
                # UP from action bar returns focus to card grid
                self.action_bar.focused = False
                for b in self.action_bar.children:
                    b.focused = False
                self._focus_only(self.card_grid)
                self.card_grid.focus_saved_or_first()
                return True
            return False

        # Card grid navigation
        if self.card_grid.on_navigate(direction):
            return True

        if dy > 0:
            # DOWN from bottom of card grid moves into action bar
            self.card_grid.focused = False
            for c in self.card_grid.children:
                c.focused = False
            self._focus_only(self.action_bar)
            self.action_bar._focus_first()
            return True

        return False

    def on_confirm(self) -> bool:
        if self.action_bar.focused or any(b.focused for b in self.action_bar.children):
            return self.action_bar.on_confirm()
        return self.card_grid.on_confirm()

    def on_mouse_click(self, position: Tuple[float, float], data: MouseClickData) -> bool:
        if not self.enabled or not self.contains(position):
            return False

        for child in reversed(self.children):
            if not child.visible or not child.enabled:
                continue

            if child.on_mouse_click(position, data):
                if child is self.action_bar:
                    self.card_grid.focused = False
                    for c in self.card_grid.children:
                        c.focused = False
                    self._focus_only(self.action_bar)
                elif child is self.card_grid:
                    self.action_bar.focused = False
                    for b in self.action_bar.children:
                        b.focused = False
                    self._focus_only(self.card_grid)
                return True

        return False