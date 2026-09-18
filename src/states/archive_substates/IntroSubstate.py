"""
P.I. Gallagher: The Missing Art

IntroSubstate — Narrative introduction for the Police Archive minigame.
Displays typewriter-effect text setting the scene for Lauren's infiltration.
"""

import pygame

from gale.state import BaseState
from gale.text import render_text

import settings
from src.data.archive_data import COLORS, INTRO_TEXT
from src.text_utils import TypewriterEffect


class IntroSubstate(BaseState):
    def __init__(self, state_machine, parent_state):
        super().__init__(state_machine)
        self.parent = parent_state
        self.typewriter = TypewriterEffect(char_speed=0.035)

    def enter(self, **kwargs):
        self.typewriter.set_text(INTRO_TEXT)
        self.alpha = 0.0

    def update(self, dt):
        if self.alpha < 255:
            self.alpha = min(255, self.alpha + 200 * dt)

        self.typewriter.update(dt)

    def on_input(self, input_id, input_data):
        if input_id == "space" and input_data.pressed:
            if not self.typewriter.finished:
                self.typewriter.complete()
            else:
                self.state_machine.change("phase_a")

    def render(self, surface):
        surface.fill(COLORS["background"])

        render_text(
            surface,
            "ARCHIVO DE LA COMISARÍA",
            settings.FONTS["large"],
            settings.VIRTUAL_WIDTH // 2,
            20,
            COLORS["brass"],
            center=True,
            shadowed=True,
        )

        render_text(
            surface,
            "— Sótano —",
            settings.FONTS["medium"],
            settings.VIRTUAL_WIDTH // 2,
            42,
            COLORS["muted"],
            center=True,
        )

        visible_lines = self.typewriter.visible_text.split("\n")
        y = 72
        for line in visible_lines:
            if line:
                render_text(
                    surface,
                    line,
                    settings.FONTS["medium"],
                    40,
                    y,
                    COLORS["paper"],
                )
            y += 18

        if self.typewriter.finished:
            render_text(
                surface,
                "ESPACIO para continuar",
                settings.FONTS["medium"],
                settings.VIRTUAL_WIDTH // 2,
                240,
                COLORS["muted"],
                center=True,
            )

        if self.alpha < 255:
            overlay = pygame.Surface(
                (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA
            )
            overlay.fill((0, 0, 0, int(255 - self.alpha)))
            surface.blit(overlay, (0, 0))