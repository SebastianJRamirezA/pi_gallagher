"""
P.I. Gallagher: The Missing Art

CorkboardState — The central investigative corkboard in Gallagher's office.
Pins clue cards with thumbtacks, connects keywords with red thread (hilo rojo),
validates deductions via StoryManager, and unlocks progressive story chapters.
"""

from typing import Any, Dict, List, Optional, Set, Tuple

import pygame

from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text

import settings
from src.data.cards import CARDS, DEDUCTIONS, LAUREN_HINTS, OPEN_QUESTIONS
from src.story.StoryManager import StoryManager


class CorkboardState(BaseState):
    # Noir Corkboard Color Palette
    COLOR_FRAME = (55, 35, 22)
    COLOR_CORK = (148, 112, 78)
    COLOR_CORK_DARK = (128, 95, 64)
    COLOR_PANEL_BG = (35, 30, 26)
    COLOR_PAPER = (235, 224, 200)
    COLOR_PAPER_SELECTED = (255, 248, 225)
    COLOR_PAPER_THREADED = (245, 215, 215)
    COLOR_INK = (30, 25, 22)
    COLOR_KEYWORD = (165, 45, 30)
    COLOR_THREAD = (210, 30, 30)
    COLOR_PIN = (220, 40, 40)
    COLOR_PIN_HEAD = (245, 180, 50)
    COLOR_BRASS = (185, 145, 65)
    COLOR_MUTED = (120, 110, 100)
    COLOR_SUCCESS = (60, 130, 60)
    COLOR_DANGER = (180, 50, 40)

    def enter(self) -> None:
        self.story = StoryManager.get_instance()
        self.visit = self.story.get_current_corcho_visit()

        # Retrieve available cards based on player's inventory
        self.cards = self.story.get_available_cards_for_corkboard()
        # Sort cards deterministically (C01, C02, etc.)
        self.cards.sort(key=lambda c: c["id"])

        self.selected_index = 0
        self.threaded_ids: List[str] = []  # IDs of cards pinned with the red thread

        # Feedback message and timer
        self.feedback_msg: str = ""
        self.feedback_timer: float = 0.0
        self.feedback_is_success: bool = False

        # Grid layout for cards on the board
        # Board area: left=10, top=32, width=335, height=195
        self.COLS = 3
        self.CARD_W = 104
        self.CARD_H = 44
        self.CARD_GAP_X = 8
        self.CARD_GAP_Y = 6
        self.BOARD_X = 14
        self.BOARD_Y = 36

        # Scroll offset if there are more cards than fit on screen
        self.scroll_row = 0

    def _get_card_pos(self, index: int) -> Tuple[int, int]:
        row = (index // self.COLS) - self.scroll_row
        col = index % self.COLS
        x = self.BOARD_X + col * (self.CARD_W + self.CARD_GAP_X)
        y = self.BOARD_Y + row * (self.CARD_H + self.CARD_GAP_Y)
        return x, y

    def _get_pin_pos(self, card_id: str) -> Optional[Tuple[int, int]]:
        for i, card in enumerate(self.cards):
            if card["id"] == card_id:
                x, y = self._get_card_pos(i)
                return x + self.CARD_W // 2, y + 4
        return None

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if not input_data.pressed:
            return

        total_cards = len(self.cards)
        if total_cards == 0:
            if input_id in ("quit", "interact", "enter"):
                self.state_machine.pop()
            return

        row = self.selected_index // self.COLS
        col = self.selected_index % self.COLS

        if input_id == "quit":
            self.state_machine.pop()
            return

        elif input_id == "move_left" and col > 0:
            self.selected_index -= 1
        elif input_id == "move_right" and col < self.COLS - 1 and self.selected_index + 1 < total_cards:
            self.selected_index += 1
        elif input_id == "move_up" and row > 0:
            self.selected_index -= self.COLS
            if self.selected_index // self.COLS < self.scroll_row:
                self.scroll_row = max(0, self.scroll_row - 1)
        elif input_id == "move_down":
            next_idx = self.selected_index + self.COLS
            if next_idx < total_cards:
                self.selected_index = next_idx
                visible_rows = 4
                if self.selected_index // self.COLS >= self.scroll_row + visible_rows:
                    self.scroll_row += 1

        elif input_id in ("interact", "confirm"):
            # Pin / unpin selected card to red thread
            card = self.cards[self.selected_index]
            cid = card["id"]
            if cid in self.threaded_ids:
                self.threaded_ids.remove(cid)
            else:
                self.threaded_ids.append(cid)

        elif input_id == "enter":
            # Enter validates current thread
            self._attempt_deduction()

        elif input_id in ("rotate_left", "rotate_right", "fine"):
            # Hotkey for Lauren's hint
            hint = LAUREN_HINTS.get(self.visit, "Lauren no tiene más pistas por ahora.")
            self.feedback_msg = hint
            self.feedback_timer = 6.0
            self.feedback_is_success = False

    def update(self, dt: float) -> None:
        if self.feedback_timer > 0:
            self.feedback_timer -= dt
            if self.feedback_timer <= 0:
                self.feedback_msg = ""

    def _attempt_deduction(self) -> None:
        if len(self.threaded_ids) < 2:
            self.feedback_msg = "Debes clavar el hilo rojo al menos entre dos tarjetas."
            self.feedback_timer = 3.5
            self.feedback_is_success = False
            return

        is_valid, ded, msg = self.story.validate_connection(self.threaded_ids)
        self.feedback_msg = msg
        self.feedback_timer = 5.0
        self.feedback_is_success = is_valid

        if is_valid:
            # Clear current thread so player can form next deduction
            self.threaded_ids.clear()
            self.visit = self.story.get_current_corcho_visit()
            # Refresh card catalog
            self.cards = self.story.get_available_cards_for_corkboard()
            self.cards.sort(key=lambda c: c["id"])

    def render(self, surface: pygame.Surface) -> None:
        # Wooden outer frame
        surface.fill(self.COLOR_FRAME)

        # Corkboard inner area
        board_rect = pygame.Rect(6, 6, settings.VIRTUAL_WIDTH - 12, settings.VIRTUAL_HEIGHT - 12)
        pygame.draw.rect(surface, self.COLOR_CORK, board_rect)

        # Subtle cork texture lines
        for i in range(12, settings.VIRTUAL_HEIGHT - 12, 16):
            pygame.draw.line(surface, self.COLOR_CORK_DARK, (8, i), (settings.VIRTUAL_WIDTH - 8, i), 1)

        # Top Header Bar
        render_text(
            surface,
            f"PIZARRA DE CORCHO — VISITA {self.visit}",
            settings.FONTS["medium"],
            14,
            10,
            self.COLOR_FRAME,
            shadowed=True,
        )

        counter_text = f"Pistas clavadas: {len(self.cards)}"
        render_text(
            surface,
            counter_text,
            settings.FONTS["small"],
            240,
            12,
            self.COLOR_FRAME,
        )

        # Draw red threads connecting selected cards
        if len(self.threaded_ids) >= 2:
            points = []
            for cid in self.threaded_ids:
                pos = self._get_pin_pos(cid)
                if pos:
                    points.append(pos)
            if len(points) >= 2:
                pygame.draw.lines(surface, self.COLOR_THREAD, False, points, 2)

        # Render cards
        for i, card in enumerate(self.cards):
            row = (i // self.COLS) - self.scroll_row
            if row < 0 or row >= 4:
                continue

            cx, cy = self._get_card_pos(i)
            card_rect = pygame.Rect(cx, cy, self.CARD_W, self.CARD_H)

            is_selected = (i == self.selected_index)
            is_threaded = (card["id"] in self.threaded_ids)

            # Card background
            if is_threaded:
                bg = self.COLOR_PAPER_THREADED
            elif is_selected:
                bg = self.COLOR_PAPER_SELECTED
            else:
                bg = self.COLOR_PAPER

            pygame.draw.rect(surface, bg, card_rect, border_radius=2)

            # Border
            if is_selected:
                pygame.draw.rect(surface, self.COLOR_PIN_HEAD, card_rect, 2, border_radius=2)
            elif is_threaded:
                pygame.draw.rect(surface, self.COLOR_THREAD, card_rect, 2, border_radius=2)
            else:
                pygame.draw.rect(surface, (150, 140, 125), card_rect, 1, border_radius=2)

            # Card thumbtack
            pin_x = cx + self.CARD_W // 2
            pin_y = cy + 4
            pin_color = self.COLOR_PIN if is_threaded else self.COLOR_PIN_HEAD
            pygame.draw.circle(surface, pin_color, (pin_x, pin_y), 3)

            # Card Title
            render_text(
                surface,
                f"[{card['id']}] {card['titulo']}",
                settings.FONTS["small"],
                cx + 4,
                cy + 8,
                self.COLOR_INK,
            )

            # Highlighted Keywords
            kw_str = ", ".join(card.get("claves", [])[:2])
            render_text(
                surface,
                kw_str,
                settings.FONTS["small"],
                cx + 4,
                cy + 24,
                self.COLOR_KEYWORD,
            )

        # Right sidebar: Column of Open Questions ("Preguntas Abiertas")
        sidebar_x = 358
        sidebar_w = settings.VIRTUAL_WIDTH - sidebar_x - 12
        sidebar_rect = pygame.Rect(sidebar_x, 32, sidebar_w, 185)
        pygame.draw.rect(surface, self.COLOR_PANEL_BG, sidebar_rect, border_radius=3)
        pygame.draw.rect(surface, self.COLOR_BRASS, sidebar_rect, 1, border_radius=3)

        render_text(
            surface,
            "DUDAS ABIERTAS",
            settings.FONTS["small"],
            sidebar_rect.centerx,
            36,
            self.COLOR_BRASS,
            center=True,
        )
        pygame.draw.line(surface, self.COLOR_BRASS, (sidebar_x + 6, 50), (sidebar_x + sidebar_w - 6, 50), 1)

        questions = OPEN_QUESTIONS.get(self.visit, [])
        qy = 54
        for q in questions:
            words = q.split()
            line1, line2 = "", ""
            for w in words:
                test = line1 + (" " if line1 else "") + w
                if settings.FONTS["small"].size(test)[0] <= sidebar_w - 12:
                    line1 = test
                else:
                    line2 += (" " if line2 else "") + w
            render_text(surface, f"• {line1}", settings.FONTS["small"], sidebar_x + 6, qy, (210, 200, 185))
            qy += 14
            if line2:
                render_text(surface, f"  {line2}", settings.FONTS["small"], sidebar_x + 6, qy, (210, 200, 185))
                qy += 14
            qy += 4

        # Bottom Feedback / Monologue Bar
        feedback_y = 222
        feedback_rect = pygame.Rect(14, feedback_y, settings.VIRTUAL_WIDTH - 28, 22)
        pygame.draw.rect(surface, (25, 20, 18), feedback_rect, border_radius=2)
        pygame.draw.rect(surface, (80, 70, 60), feedback_rect, 1, border_radius=2)

        if self.feedback_msg:
            fb_color = self.COLOR_SUCCESS if self.feedback_is_success else self.COLOR_DANGER
            render_text(
                surface,
                self.feedback_msg,
                settings.FONTS["small"],
                feedback_rect.x + 8,
                feedback_y + 4,
                fb_color,
            )
        else:
            render_text(
                surface,
                "Flechas: Mover   ESPACIO: Clavar hilo   ENTER: Deducir   H: Ayuda Lauren   ESC: Salir",
                settings.FONTS["small"],
                feedback_rect.centerx,
                feedback_y + 4,
                self.COLOR_MUTED,
                center=True,
            )

