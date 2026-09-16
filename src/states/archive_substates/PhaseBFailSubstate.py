"""
P.I. Gallagher: The Missing Art

PhaseBFailSubstate — Failure screen for Phase B.
Shown when the clock runs out before all 3 clues are collected.
Resets Phase B progress but keeps Phase A completion.
"""

import pygame

from gale.state import BaseState
from gale.input_handler import InputData
from gale.text import render_text

import settings
from src.data.archive_data import COLORS, PHASE_B_FAIL_TEXT


class PhaseBFailSubstate(BaseState):
    def __init__(self, state_machine, parent_state):
        super().__init__(state_machine)
        self.parent = parent_state

    def enter(self, **kwargs):
        # Reset Phase B progress (Phase A stays completed)
        self.parent.collected_clues.clear()
        self.alpha = 0.0
        self.wait_timer = 2.5
        self.can_continue = False

    def update(self, dt):
        if self.alpha < 220:
            self.alpha = min(220, self.alpha + 150 * dt)

        if not self.can_continue:
            self.wait_timer -= dt
            if self.wait_timer <= 0:
                self.can_continue = True

    def on_input(self, input_id, input_data):
        if self.can_continue and input_id == "confirm" and input_data.pressed:
            # if getattr(self.parent, "door", None) is not None:
            #     self.parent.door.active = True
            self.parent.state_machine.pop()

    def render(self, surface):
        surface.fill(COLORS["background"])

        # Dark overlay fade
        if self.alpha > 0:
            overlay = pygame.Surface(
                (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA
            )
            overlay.fill((0, 0, 0, int(self.alpha)))
            surface.blit(overlay, (0, 0))

        # Fail text
        lines = PHASE_B_FAIL_TEXT.split("\n")
        y = 95
        for line in lines:
            if line:
                render_text(
                    surface,
                    line,
                    settings.FONTS["medium"],
                    settings.VIRTUAL_WIDTH // 2,
                    y,
                    COLORS["paper"],
                    center=True,
                )
            y += 24

        # Prompt
        if self.can_continue:
            render_text(
                surface,
                "ESPACIO para reintentar",
                settings.FONTS["small"],
                settings.VIRTUAL_WIDTH // 2,
                200,
                COLORS["muted"],
                center=True,
            )
