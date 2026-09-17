"""
P.I. Gallagher: The Missing Art

CorkboardState — Central investigative corkboard built entirely on gale.ui.
Features 2D grid navigation across clue cards, seamless focus transition to bottom
action buttons, mouse click and motion support, a dedicated full-screen Card Details
overlay, and modal dialogs for deductions and Lauren's hints.
"""

from typing import Optional


from gale.ui import Button, Container
from gale.ui.widget import Direction

from src.ui import CardButton

class CardGridContainer(Container):
    """
    gale.ui.Container organizing CardButtons in a 2-column grid.
    Supports clean 4-way arrow navigation and yields focus downwards on the bottom row.
    """

    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        cols: int = 2,
        **kwargs,
    ) -> None:
        super().__init__(x, y, width, height, **kwargs)
        self.cols = cols
        self.last_focused_index: int = 0

    def get_focused_card_button(self) -> Optional[CardButton]:
        for child in self.children:
            if isinstance(child, CardButton) and child.focused:
                return child
        if self.children and isinstance(self.children[0], CardButton):
            idx = max(0, min(self.last_focused_index, len(self.children) - 1))
            return self.children[idx]  # type: ignore[return-value]
        return None

    def focus_saved_or_first(self) -> None:
        focusable = self._focusable_children()
        if not focusable:
            return
        idx = max(0, min(self.last_focused_index, len(focusable) - 1))
        self._focus_only(focusable[idx])

    def _move_focus(self, direction: Direction) -> bool:
        focusable = self._focusable_children()
        if not focusable:
            return False

        dx, dy = direction
        current = self._focused_child()
        current_index = focusable.index(current) if current in focusable else self.last_focused_index
        total = len(focusable)

        row = current_index // self.cols
        col = current_index % self.cols

        if dx != 0:
            next_col = col + dx
            next_idx = row * self.cols + next_col
            if 0 <= next_col < self.cols and 0 <= next_idx < total:
                self.last_focused_index = next_idx
                self._focus_only(focusable[next_idx])
                return True
            return False
        elif dy != 0:
            next_row = row + dy
            next_idx = next_row * self.cols + col
            if 0 <= next_idx < total:
                self.last_focused_index = next_idx
                self._focus_only(focusable[next_idx])
                return True
            # When moving down past the bottom row, return False to let parent transfer focus to action bar
            return False

        return False