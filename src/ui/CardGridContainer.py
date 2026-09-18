"""
P.I. Gallagher: The Missing Art

"""

from typing import Optional


from gale.ui import Button, Container
from gale.ui.widget import Direction
from gale.text import render_text
import pygame
import settings

from src.ui import CardButton
from src.ui.theme import COLOR_BRASS_LIGHT

class CardGridContainer(Container):
    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        cols: int = 2,
        visible_rows: int = 3,
        card_w: int = 152,
        card_h: int = 50,
        gap_x: int = 8,
        gap_y: int = 4,
        **kwargs,
    ) -> None:
        super().__init__(x, y, width, height, **kwargs)
        self.cols = cols
        self.visible_rows = visible_rows
        self.card_w = card_w
        self.card_h = card_h
        self.gap_x = gap_x
        self.gap_y = gap_y
        self.last_focused_index: int = 0
        self.scroll_offset: int = 0

    def get_focused_card_button(self) -> Optional[CardButton]:
        card_buttons = [c for c in self.children if isinstance(c, CardButton)]
        for child in card_buttons:
            if child.focused:
                return child
        if card_buttons:
            idx = max(0, min(self.last_focused_index, len(card_buttons) - 1))
            return card_buttons[idx]
        return None

    def focus_saved_or_first(self) -> None:
        card_buttons = [c for c in self.children if isinstance(c, CardButton)]
        if not card_buttons:
            return
        idx = max(0, min(self.last_focused_index, len(card_buttons) - 1))
        self._update_scroll_position(idx)
        self._focus_only(card_buttons[idx])

    def _update_scroll_position(self, target_idx: int) -> None:
        card_buttons = [c for c in self.children if isinstance(c, CardButton)]
        total_cards = len(card_buttons)

        # 1D Horizontal Overflow Scrolling (Single Row)
        if self.visible_rows == 1:
            visible_capacity = self.cols
            if target_idx < self.scroll_offset:
                self.scroll_offset = target_idx
            elif target_idx >= self.scroll_offset + visible_capacity:
                self.scroll_offset = target_idx - visible_capacity + 1

            self.can_scroll_left = self.scroll_offset > 0
            self.can_scroll_right = (self.scroll_offset + visible_capacity) < total_cards

            for i, btn in enumerate(card_buttons):
                if self.scroll_offset <= i < self.scroll_offset + visible_capacity:
                    btn.visible = True
                    visible_idx = i - self.scroll_offset
                    new_x = int(self.rect.x + visible_idx * (self.card_w + self.gap_x))
                    new_y = int(self.rect.y)
                    btn.rect.x = new_x
                    btn.rect.y = new_y
                    btn.x = new_x
                    btn.y = new_y
                else:
                    btn.visible = False
            return

        # 2D Grid Vertical Overflow Scrolling
        target_row = target_idx // self.cols
        if target_row < self.scroll_offset:
            self.scroll_offset = target_row
        elif target_row >= self.scroll_offset + self.visible_rows:
            self.scroll_offset = target_row - self.visible_rows + 1

        total_rows = (total_cards + self.cols - 1) // self.cols
        self.can_scroll_up = self.scroll_offset > 0
        self.can_scroll_down = (self.scroll_offset + self.visible_rows) < total_rows

        for i, btn in enumerate(card_buttons):
            row = i // self.cols
            col = i % self.cols

            if self.scroll_offset <= row < self.scroll_offset + self.visible_rows:
                btn.visible = True
                visible_row = row - self.scroll_offset
                new_x = int(self.rect.x + col * (self.card_w + self.gap_x))
                new_y = int(self.rect.y + visible_row * (self.card_h + self.gap_y))
                btn.rect.x = new_x
                btn.rect.y = new_y
                btn.x = new_x
                btn.y = new_y
            else:
                btn.visible = False

    def render(self, surface: pygame.Surface) -> None:
        super().render(surface)

        color = pygame.Color(230, 175, 45)

        # Render Horizontal Left/Right Arrows for 1-row layout
        if self.visible_rows == 1:
            arrow_y = int(self.rect.y + self.card_h / 2)

            if getattr(self, "can_scroll_left", False):
                left_x = int(self.rect.x - 10)
                points = [
                    (left_x, arrow_y),
                    (left_x + 8, arrow_y - 6),
                    (left_x + 8, arrow_y + 6),
                ]
                pygame.draw.polygon(surface, color, points)

            if getattr(self, "can_scroll_right", False):
                right_x = int(self.rect.x + (self.cols * (self.card_w + self.gap_x)) + 2)
                points = [
                    (right_x + 8, arrow_y),
                    (right_x, arrow_y - 6),
                    (right_x, arrow_y + 6),
                ]
                pygame.draw.polygon(surface, color, points)

            return

        # Render Vertical Up/Down Arrows for corkboard 2D grid
        arrow_x = int(self.rect.x + (self.cols * (self.card_w + self.gap_x) - self.gap_x) / 2 - 3)
        if getattr(self, "can_scroll_up", False):
            top_y = self.rect.y
            points = [
                (arrow_x + 3, top_y - 12),
                (arrow_x, top_y - 3),
                (arrow_x + 6, top_y - 3),
            ]
            pygame.draw.polygon(surface, color, points)

        if getattr(self, "can_scroll_down", False):
            bottom_y = int(self.rect.y + (self.card_h + self.gap_y) * self.visible_rows)
            points = [
                (arrow_x + 3, bottom_y + 12),
                (arrow_x, bottom_y + 3),
                (arrow_x + 6, bottom_y + 3),
            ]
            pygame.draw.polygon(surface, color, points)

    def _move_focus(self, direction: Direction) -> bool:
        card_buttons = [c for c in self.children if isinstance(c, CardButton)]
        if not card_buttons:
            return False

        dx, dy = direction
        current = self._focused_child()
        current_index = card_buttons.index(current) if current in card_buttons else self.last_focused_index
        total = len(card_buttons)

        # Navigation logic for 1D Horizontal layout
        if self.visible_rows == 1:
            step = dx if dx != 0 else dy
            next_idx = current_index + step
            if 0 <= next_idx < total:
                self.last_focused_index = next_idx
                self._update_scroll_position(next_idx)
                self._focus_only(card_buttons[next_idx])
                return True
            return False

        # Navigation logic for 2D Grid layout
        row = current_index // self.cols
        col = current_index % self.cols

        if dx != 0:
            next_col = col + dx
            next_idx = row * self.cols + next_col
            if 0 <= next_col < self.cols and 0 <= next_idx < total:
                self.last_focused_index = next_idx
                self._update_scroll_position(next_idx)
                self._focus_only(card_buttons[next_idx])
                return True
            return False
        elif dy != 0:
            next_row = row + dy
            next_idx = next_row * self.cols + col

            if next_row * self.cols >= total and total % self.cols != 0 and next_row == (total // self.cols):
                next_idx = total - 1

            if 0 <= next_idx < total:
                self.last_focused_index = next_idx
                self._update_scroll_position(next_idx)
                self._focus_only(card_buttons[next_idx])
                return True
            return False

        return False