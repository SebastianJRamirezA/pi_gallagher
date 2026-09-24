import random
import pygame

from gale.state import BaseState
from gale.input_handler import InputData
from gale.text import render_text

import settings
from src.data.archive_data import COLORS, CABINET, CATEGORY_ORDER, MAX_DRAWERS


class PhaseASubstate(BaseState):
    def __init__(self, state_machine, parent_state):
        super().__init__(state_machine)
        self.parent = parent_state

    def enter(self, **kwargs):
        self.selected_cat = 0
        self.selected_drawer = 0
        self.drawers_opened = 0
        self.opened_set = set()  # (cat_index, drawer_index) tuples
        self.viewing_card = False
        self.current_card = None
        self.found_goal = False

        # Layout constants
        self.COL_X = [15, 167, 319]
        self.COL_WIDTH = 140
        self.HEADER_Y = 32
        self.DRAWER_START_Y = 55
        self.DRAWER_HEIGHT = 38
        self.DRAWER_GAP = 4

    def _get_drawers(self, cat_index):
        cat_name = CATEGORY_ORDER[cat_index]
        return CABINET[cat_name]["drawers"]

    def _get_drawer_rect(self, cat_index, drawer_index):
        x = self.COL_X[cat_index]
        y = self.DRAWER_START_Y + drawer_index * (self.DRAWER_HEIGHT + self.DRAWER_GAP)
        return pygame.Rect(x, y, self.COL_WIDTH, self.DRAWER_HEIGHT)

    # ── Input ──────────────────────────────────────────────────────────────

    def on_input(self, input_id, input_data):
        if not input_data.pressed:
            return

        # Card overlay is open — close it and check win/fail
        if self.viewing_card:
            if input_id == "space":
                settings.SOUNDS["bookClose"].play()
                self.viewing_card = False
                self.current_card = None
                if self.found_goal:
                    self.parent.expedition_found = True
                    self.state_machine.change("phase_b")
                elif self.drawers_opened >= MAX_DRAWERS:
                    self.state_machine.change("phase_a_fail")
            return

        # Navigation
        moved = False
        if input_id == "move_left":
            self.selected_cat = max(0, self.selected_cat - 1)
            max_d = len(self._get_drawers(self.selected_cat)) - 1
            self.selected_drawer = min(self.selected_drawer, max_d)
            moved = True
        elif input_id == "move_right":
            self.selected_cat = min(len(CATEGORY_ORDER) - 1, self.selected_cat + 1)
            max_d = len(self._get_drawers(self.selected_cat)) - 1
            self.selected_drawer = min(self.selected_drawer, max_d)
            moved = True
        elif input_id == "move_up":
            self.selected_drawer = max(0, self.selected_drawer - 1)
            moved = True
        elif input_id == "move_down":
            max_d = len(self._get_drawers(self.selected_cat)) - 1
            self.selected_drawer = min(max_d, self.selected_drawer + 1)
            moved = True
        elif input_id == "space":
            self._open_drawer()

        if moved:
            settings.SOUNDS[f"bookFlip{random.randint(1, 3)}"].play()

    def _open_drawer(self):
        # Play drawer/card open sound effect
        settings.SOUNDS[f"bookPlace{random.randint(1, 3)}"].play()

        key = (self.selected_cat, self.selected_drawer)
        drawers = self._get_drawers(self.selected_cat)
        self.current_card = drawers[self.selected_drawer]
        self.viewing_card = True

        # Only count as new opening if not previously opened
        if key not in self.opened_set:
            self.drawers_opened += 1
            self.opened_set.add(key)

        if self.current_card["is_goal"]:
            self.found_goal = True

    # ── Render ─────────────────────────────────────────────────────────────

    def render(self, surface):
        surface.fill(COLORS["background"])

        # Header title
        render_text(
            surface,
            "MUEBLE FICHERO",
            settings.FONTS["large"],
            12,
            8,
            COLORS["brass"],
            shadowed=True,
        )

        # Drawer counter (right-aligned)
        remaining = MAX_DRAWERS - self.drawers_opened
        status = f"Cajones restantes: {remaining}/{MAX_DRAWERS}"
        status_w = settings.FONTS["medium"].size(status)[0]
        render_text(
            surface,
            status,
            settings.FONTS["medium"],
            settings.VIRTUAL_WIDTH - status_w - 12,
            12,
            COLORS["danger"] if remaining <= 1 else COLORS["muted"],
        )

        # Draw each category column
        for cat_i, cat_name in enumerate(CATEGORY_ORDER):
            cat_data = CABINET[cat_name]
            col_x = self.COL_X[cat_i]
            is_selected_cat = cat_i == self.selected_cat

            # Column header
            header_rect = pygame.Rect(col_x, self.HEADER_Y, self.COL_WIDTH, 18)
            header_color = COLORS["brass"] if is_selected_cat else COLORS["panel_light"]
            pygame.draw.rect(surface, header_color, header_rect, border_radius=2)
            render_text(
                surface,
                cat_data["label"],
                settings.FONTS["medium"],
                col_x + self.COL_WIDTH // 2,
                self.HEADER_Y + 2,
                COLORS["ink"] if is_selected_cat else COLORS["muted"],
                center=True,
            )

            # Drawers
            for d_i, drawer in enumerate(cat_data["drawers"]):
                rect = self._get_drawer_rect(cat_i, d_i)
                key = (cat_i, d_i)
                is_opened = key in self.opened_set
                is_selected = (
                    cat_i == self.selected_cat
                    and d_i == self.selected_drawer
                    and not self.viewing_card
                )

                # Drawer background
                bg = COLORS["panel"] if is_opened else COLORS["panel_light"]
                pygame.draw.rect(surface, bg, rect, border_radius=2)

                # Selection highlight
                if is_selected:
                    pygame.draw.rect(surface, COLORS["brass"], rect, 2, border_radius=2)
                    # Selection arrow
                    ax = rect.x - 8
                    ay = rect.centery
                    pygame.draw.polygon(
                        surface,
                        COLORS["brass"],
                        [(ax, ay - 4), (ax + 6, ay), (ax, ay + 4)],
                    )
                else:
                    pygame.draw.rect(
                        surface, COLORS["brass_dark"], rect, 1, border_radius=2
                    )

                # Drawer label
                label_color = COLORS["muted"] if is_opened else COLORS["paper"]
                render_text(
                    surface,
                    drawer["label"],
                    settings.FONTS["medium"],
                    rect.x + 8,
                    rect.y + 6,
                    label_color,
                )

                # Reference hint on drawer (small text)
                if drawer["reference"] and not is_opened:
                    render_text(
                        surface,
                        "ref.",
                        settings.FONTS["medium"],
                        rect.right - 28,
                        rect.y + 22,
                        COLORS["text_dark"],
                    )

                # Opened indicator
                if is_opened:
                    render_text(
                        surface,
                        "[abierto]",
                        settings.FONTS["medium"],
                        rect.x + 8,
                        rect.y + 22,
                        COLORS["text_dark"],
                    )

        # Controls hint
        render_text(
            surface,
            "Flechas: Navegar   ESPACIO: Abrir cajón",
            settings.FONTS["medium"],
            settings.VIRTUAL_WIDTH // 2,
            252,
            COLORS["muted"],
            center=True,
        )

        # Card overlay
        if self.viewing_card and self.current_card:
            self._render_card(surface)

    def _render_card(self, surface):
        """Render the index card overlay for the opened drawer."""
        # Semi-transparent background
        overlay = pygame.Surface(
            (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        # Card panel
        cx, cy, cw, ch = 65, 30, 350, 200
        card_rect = pygame.Rect(cx, cy, cw, ch)
        pygame.draw.rect(surface, COLORS["paper"], card_rect, border_radius=3)
        pygame.draw.rect(surface, COLORS["brass_dark"], card_rect, 2, border_radius=3)

        # Card header
        render_text(
            surface,
            "FICHA DE ÍNDICE",
            settings.FONTS["medium"],
            card_rect.centerx,
            cy + 8,
            COLORS["brass_dark"],
            center=True,
        )

        # Separator
        pygame.draw.line(
            surface,
            COLORS["brass_dark"],
            (cx + 10, cy + 24),
            (cx + cw - 10, cy + 24),
            1,
        )

        # Drawer label
        render_text(
            surface,
            self.current_card["label"],
            settings.FONTS["large"],
            cx + 15,
            cy + 30,
            COLORS["ink"],
        )

        # Body text with reference highlighting
        lines = self.current_card["text"].split("\n")
        y = cy + 55
        for line in lines:
            if line.strip():
                if line.startswith("Véase:") or line.startswith(">>>"):
                    color = COLORS["highlight"]
                else:
                    color = COLORS["ink"]
                render_text(
                    surface,
                    line,
                    settings.FONTS["medium"],
                    cx + 15,
                    y,
                    color,
                )
                y += 15
            else:
                y += 8

        # Bottom prompt
        if self.found_goal:
            render_text(
                surface,
                "EXPEDIENTE LOCALIZADO",
                settings.FONTS["medium"],
                card_rect.centerx,
                card_rect.bottom - 32,
                COLORS["success"],
                center=True,
            )
        render_text(
            surface,
            "ESPACIO para continuar",
            settings.FONTS["medium"],
            card_rect.centerx,
            card_rect.bottom - 14,
            COLORS["muted"],
            center=True,
        )
