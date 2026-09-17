"""
P.I. Gallagher: The Missing Art

CorkboardState — Central investigative corkboard built entirely on gale.ui.
Features 2D grid navigation across clue cards, seamless focus transition to bottom
action buttons and motion support, a dedicated full-screen Card Details
overlay, and modal dialogs for deductions and Lauren's hints.
"""

from typing import Callable, Optional, Tuple

import pygame

from gale.ui import Container, Window
from gale.ui.widget import Direction

class ModalOverlay(Container):
    """
    Full-screen modal container that isolates modal windows (details & dialogue).
    """

    def __init__(
        self,
        width: float,
        height: float,
        window: Window,
        on_dismiss: Optional[Callable[[], None]] = None,
    ) -> None:
        super().__init__(0, 0, width, height)
        self.window = window
        self.on_dismiss = on_dismiss
        self.add_child(window)
        if window._focusable_children():
            window._focus_first()
        self.focused = True

    def on_navigate(self, direction: Direction) -> bool:
        return self.window.on_navigate(direction)

    def on_confirm(self) -> bool:
        return self.window.on_confirm()

    def render(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return

        overlay = pygame.Surface((int(self.width), int(self.height)), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))
        self.window.render(surface)