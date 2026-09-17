"""
P.I. Gallagher: The Missing Art

PhaseBSubstate — Document Table phase.
Examine documents on a desk to find 3 key clues (C02, C03, C12) before time
runs out. Irrelevant documents consume extra time.
"""

import math
import random

import pygame

from gale.state import BaseState
from gale.input_handler import InputData
from gale.text import render_text
from gale.timer import Timer

import settings
from src.data.archive_data import (
    COLORS,
    CLUES,
    PHASE_B_DOCUMENTS,
    PHASE_B_TIME_LIMIT,
    PHASE_B_TIME_PENALTY,
    REQUIRED_CLUES,
    render_keyword_line,
)


class PhaseBSubstate(BaseState):
    def __init__(self, state_machine, parent_state):
        super().__init__(state_machine)
        self.parent = parent_state

    def enter(self, **kwargs):
        # Shuffle documents so layout varies each attempt
        self.shuffled_docs = list(PHASE_B_DOCUMENTS)
        random.shuffle(self.shuffled_docs)

        self.selected_doc = 0
        self.viewing_doc = False
        self.current_doc = None
        self.examined_set = set()   # doc IDs already opened
        self.time_remaining = PHASE_B_TIME_LIMIT
        self.clock_timer_ref = None

        # Intro transition screen before the clock starts
        self.show_intro = True
        self.intro_timer = 3.5

        # Layout
        self.DOC_COLS = 4
        self.DOC_ROWS = 2
        self.DOC_WIDTH = 108
        self.DOC_HEIGHT = 78
        self.DOC_GAP_X = 5
        self.DOC_GAP_Y = 5
        self.GRID_START_X = 12
        self.GRID_START_Y = 50

    def exit(self):
        if self.clock_timer_ref:
            self.clock_timer_ref.remove()
            self.clock_timer_ref = None

    # ── Clock ──────────────────────────────────────────────────────────────

    def _start_clock(self):
        self.show_intro = False

        def tick():
            self.time_remaining -= 1
            if 0 < self.time_remaining <= 5:
                settings.SOUNDS["clock"].play()
            if self.time_remaining <= 0:
                self.time_remaining = 0
                if self.clock_timer_ref:
                    self.clock_timer_ref.remove()
                    self.clock_timer_ref = None
                self.state_machine.change("phase_b_fail")

        self.clock_timer_ref = Timer.every(1, tick)

    # ── Update ─────────────────────────────────────────────────────────────

    def update(self, dt):
        if self.show_intro:
            self.intro_timer -= dt
            if self.intro_timer <= 0:
                self._start_clock()

    # ── Input ──────────────────────────────────────────────────────────────

    def on_input(self, input_id, input_data):
        if not input_data.pressed:
            return

        # Intro screen — skip with confirm
        if self.show_intro:
            if input_id == "confirm":
                self._start_clock()
            return

        # Document view overlay
        if self.viewing_doc:
            if input_id == "confirm":
                doc = self.current_doc
                clue_id = doc.get("clue_id")
                # Collect clue if relevant and not yet collected
                if doc["is_relevant"] and clue_id and clue_id not in self.parent.collected_clues:
                    self.parent.collected_clues.append(clue_id)
                    # Check win condition
                    if all(c in self.parent.collected_clues for c in REQUIRED_CLUES):
                        if self.clock_timer_ref:
                            self.clock_timer_ref.remove()
                            self.clock_timer_ref = None
                        self.state_machine.change("success")
                        return
                # Close document
                self.viewing_doc = False
                self.current_doc = None
            return

        # Grid navigation
        col = self.selected_doc % self.DOC_COLS
        row = self.selected_doc // self.DOC_COLS

        if input_id == "move_left" and col > 0:
            self.selected_doc -= 1
        elif input_id == "move_right" and col < self.DOC_COLS - 1:
            next_idx = self.selected_doc + 1
            if next_idx < len(self.shuffled_docs):
                self.selected_doc = next_idx
        elif input_id == "move_up" and row > 0:
            self.selected_doc -= self.DOC_COLS
        elif input_id == "move_down" and row < self.DOC_ROWS - 1:
            next_idx = self.selected_doc + self.DOC_COLS
            if next_idx < len(self.shuffled_docs):
                self.selected_doc = next_idx
        elif input_id == "confirm":
            self._examine_document()

    def _examine_document(self):
        doc = self.shuffled_docs[self.selected_doc]
        self.current_doc = doc

        # First examination of an irrelevant document applies a time penalty
        if doc["id"] not in self.examined_set:
            self.examined_set.add(doc["id"])
            if not doc["is_relevant"]:
                self.time_remaining = max(0, self.time_remaining - PHASE_B_TIME_PENALTY)
                if self.time_remaining <= 0:
                    if self.clock_timer_ref:
                        self.clock_timer_ref.remove()
                        self.clock_timer_ref = None
                    self.state_machine.change("phase_b_fail")
                    return

        self.viewing_doc = True

    def _get_doc_rect(self, index):
        col = index % self.DOC_COLS
        row = index // self.DOC_COLS
        x = self.GRID_START_X + col * (self.DOC_WIDTH + self.DOC_GAP_X)
        y = self.GRID_START_Y + row * (self.DOC_HEIGHT + self.DOC_GAP_Y)
        return pygame.Rect(x, y, self.DOC_WIDTH, self.DOC_HEIGHT)

    # ── Render ─────────────────────────────────────────────────────────────

    def render(self, surface):
        surface.fill(COLORS["background"])

        if self.show_intro:
            self._render_intro(surface)
            return

        self._render_header(surface)
        self._render_clock(surface)
        self._render_grid(surface)

        # Controls hint
        hint_y = (
            self.GRID_START_Y
            + self.DOC_ROWS * (self.DOC_HEIGHT + self.DOC_GAP_Y)
            + 8
        )
        render_text(
            surface,
            "Flechas: Seleccionar   ESPACIO: Examinar",
            settings.FONTS["medium"],
            settings.VIRTUAL_WIDTH // 2,
            min(hint_y, 250),
            COLORS["muted"],
            center=True,
        )

        # Document view overlay (on top of everything)
        if self.viewing_doc and self.current_doc:
            self._render_document(surface)

    # ── Sub-renderers ──────────────────────────────────────────────────────

    def _render_intro(self, surface):
        """Transition screen showing the located expedition before Phase B."""
        render_text(
            surface,
            "EXPEDIENTE LOCALIZADO",
            settings.FONTS["large"],
            settings.VIRTUAL_WIDTH // 2,
            25,
            COLORS["success"],
            center=True,
            shadowed=True,
        )

        render_text(
            surface,
            "Exp. #12-03-MR",
            settings.FONTS["large"],
            settings.VIRTUAL_WIDTH // 2,
            60,
            COLORS["brass"],
            center=True,
        )

        # Reference card visual
        card_rect = pygame.Rect(115, 85, 250, 80)
        pygame.draw.rect(surface, COLORS["paper"], card_rect, border_radius=3)
        pygame.draw.rect(surface, COLORS["brass_dark"], card_rect, 2, border_radius=3)

        ref_lines = [
            "Del Roscio, Museo",
            "Robo de obra de arte",
            "Denuncia: 13/03/1932",
            "Asignado: Comisaría Central",
        ]
        y = card_rect.y + 10
        for line in ref_lines:
            render_text(
                surface,
                line,
                settings.FONTS["medium"],
                card_rect.centerx,
                y,
                COLORS["ink"],
                center=True,
            )
            y += 16

        render_text(
            surface,
            "Lauren lleva el expediente a la mesa...",
            settings.FONTS["medium"],
            settings.VIRTUAL_WIDTH // 2,
            195,
            COLORS["paper"],
            center=True,
        )
        render_text(
            surface,
            "ESPACIO para continuar",
            settings.FONTS["medium"],
            settings.VIRTUAL_WIDTH // 2,
            230,
            COLORS["muted"],
            center=True,
        )

    def _render_header(self, surface):
        """Top bar: expedition reference, clue counter."""
        render_text(
            surface,
            "Exp. #12-03-MR",
            settings.FONTS["large"],
            12,
            5,
            COLORS["brass"],
            shadowed=True,
        )

        collected = sum(
            1 for c in REQUIRED_CLUES if c in self.parent.collected_clues
        )
        clue_color = COLORS["success"] if collected == len(REQUIRED_CLUES) else COLORS["text"]
        render_text(
            surface,
            f"Pistas: {collected}/{len(REQUIRED_CLUES)}",
            settings.FONTS["medium"],
            12,
            28,
            clue_color,
        )

        # Time text near clock
        minutes = int(self.time_remaining) // 60
        seconds = int(self.time_remaining) % 60
        time_color = COLORS["danger"] if self.time_remaining <= 15 else COLORS["text"]
        time_str = f"{minutes}:{seconds:02d}"
        tw = settings.FONTS["medium"].size(time_str)[0]
        render_text(
            surface,
            time_str,
            settings.FONTS["medium"],
            settings.VIRTUAL_WIDTH - tw - 48,
            5,
            time_color,
        )

    def _render_clock(self, surface):
        """Analog clock showing remaining time."""
        cx = settings.VIRTUAL_WIDTH - 28
        cy = 28
        radius = 20

        # Face
        pygame.draw.circle(surface, COLORS["panel_light"], (cx, cy), radius)
        pygame.draw.circle(surface, COLORS["brass"], (cx, cy), radius, 2)

        # Hour marks
        for i in range(12):
            angle = math.radians(i * 30 - 90)
            ir = radius - 4
            orr = radius - 1
            x1 = cx + math.cos(angle) * ir
            y1 = cy + math.sin(angle) * ir
            x2 = cx + math.cos(angle) * orr
            y2 = cy + math.sin(angle) * orr
            pygame.draw.line(
                surface,
                COLORS["brass_dark"],
                (int(x1), int(y1)),
                (int(x2), int(y2)),
                1,
            )

        # Hand sweeps clockwise as time elapses
        elapsed = 1.0 - (self.time_remaining / PHASE_B_TIME_LIMIT)
        hand_angle = math.radians(elapsed * 360 - 90)
        hand_len = radius - 6
        hx = cx + math.cos(hand_angle) * hand_len
        hy = cy + math.sin(hand_angle) * hand_len
        hand_color = COLORS["danger"] if self.time_remaining <= 15 else COLORS["brass"]
        pygame.draw.line(surface, hand_color, (cx, cy), (int(hx), int(hy)), 2)
        pygame.draw.circle(surface, hand_color, (cx, cy), 2)

    def _render_grid(self, surface):
        """Document grid: 4 columns x 2 rows."""
        for i, doc in enumerate(self.shuffled_docs):
            rect = self._get_doc_rect(i)
            is_selected = i == self.selected_doc
            is_examined = doc["id"] in self.examined_set
            is_collected = doc.get("clue_id") in self.parent.collected_clues

            # Background
            if is_collected:
                bg = (55, 90, 55)
            elif is_examined:
                bg = COLORS["panel"]
            else:
                bg = COLORS["paper_dark"]
            pygame.draw.rect(surface, bg, rect, border_radius=2)

            # Border
            if is_selected:
                pygame.draw.rect(surface, COLORS["brass"], rect, 2, border_radius=2)
            else:
                pygame.draw.rect(
                    surface, COLORS["brass_dark"], rect, 1, border_radius=2
                )

            # Title (word-wrapped to fit cell)
            title = doc["title"]
            title_color = COLORS["ink"] if not is_examined else COLORS["muted"]
            if is_collected:
                title_color = COLORS["paper"]

            words = title.split()
            line1 = ""
            line2 = ""
            for word in words:
                test = line1 + (" " if line1 else "") + word
                if settings.FONTS["medium"].size(test)[0] <= rect.width - 12:
                    line1 = test
                else:
                    line2 += (" " if line2 else "") + word

            render_text(
                surface,
                line1,
                settings.FONTS["medium"],
                rect.x + 6,
                rect.y + 8,
                title_color,
            )
            if line2:
                render_text(
                    surface,
                    line2,
                    settings.FONTS["medium"],
                    rect.x + 6,
                    rect.y + 24,
                    title_color,
                )

            # Status label
            if is_collected:
                render_text(
                    surface,
                    "[OBTENIDA]",
                    settings.FONTS["medium"],
                    rect.x + 6,
                    rect.y + rect.height - 18,
                    COLORS["success"],
                )
            elif is_examined and not doc["is_relevant"]:
                render_text(
                    surface,
                    "[leído]",
                    settings.FONTS["medium"],
                    rect.x + 6,
                    rect.y + rect.height - 18,
                    COLORS["text_dark"],
                )

    def _render_document(self, surface):
        """Full-screen document examination overlay."""
        # Dark overlay
        overlay = pygame.Surface(
            (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 170))
        surface.blit(overlay, (0, 0))

        # Document panel
        dx, dy, dw, dh = 30, 10, 420, 245
        doc_rect = pygame.Rect(dx, dy, dw, dh)
        pygame.draw.rect(surface, COLORS["paper"], doc_rect, border_radius=3)
        pygame.draw.rect(surface, COLORS["brass_dark"], doc_rect, 2, border_radius=3)

        doc = self.current_doc

        # Title
        render_text(
            surface,
            doc["title"],
            settings.FONTS["large"],
            doc_rect.centerx,
            dy + 10,
            COLORS["ink"],
            center=True,
        )

        # Separator
        pygame.draw.line(
            surface,
            COLORS["brass_dark"],
            (dx + 10, dy + 30),
            (dx + dw - 10, dy + 30),
            1,
        )

        # Body text with keyword highlighting
        lines = doc["body"].split("\n")
        y = dy + 38
        for line in lines:
            if line:
                render_keyword_line(
                    surface,
                    line,
                    settings.FONTS["medium"],
                    dx + 15,
                    y,
                    COLORS["ink"],
                    COLORS["highlight"],
                )
                y += 14
            else:
                y += 8

        # Prompt at bottom
        clue_id = doc.get("clue_id")
        if doc["is_relevant"] and clue_id and clue_id not in self.parent.collected_clues:
            prompt = "ESPACIO: Recolectar pista"
            prompt_color = COLORS["highlight"]
        elif doc["is_relevant"] and clue_id and clue_id in self.parent.collected_clues:
            prompt = "Pista ya obtenida - ESPACIO: Cerrar"
            prompt_color = COLORS["muted"]
        else:
            prompt = "Sin pistas relevantes - ESPACIO: Cerrar"
            prompt_color = COLORS["muted"]

        render_text(
            surface,
            prompt,
            settings.FONTS["medium"],
            doc_rect.centerx,
            doc_rect.bottom - 14,
            prompt_color,
            center=True,
        )
