"""
P.I. Gallagher: The Missing Art

CorkboardState — Central investigative corkboard built entirely on gale.ui.
Features 2D grid navigation across clue cards, seamless focus transition to bottom
action buttons, mouse click and motion support, a dedicated full-screen Card Details
overlay, and modal dialogs for deductions and Lauren's hints.
"""


from gale.ui import Container
from gale.ui.widget import Direction

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



class ActionBarContainer(Container):
    """
    gale.ui.Container organizing action buttons horizontally.
    Supports left/right wrapping and yields focus upwards on UP arrow.
    """

    def __init__(self, x: float, y: float, width: float, height: float, **kwargs) -> None:
        super().__init__(x, y, width, height, **kwargs)

    def _move_focus(self, direction: Direction) -> bool:
        focusable = self._focusable_children()
        if not focusable:
            return False

        dx, dy = direction
        if dy < 0:
            # Pressing UP yields focus back to the card grid
            return False

        if dx != 0:
            current = self._focused_child()
            current_index = focusable.index(current) if current in focusable else 0
            next_index = (current_index + dx) % len(focusable)
            self._focus_only(focusable[next_index])
            return True

        return False