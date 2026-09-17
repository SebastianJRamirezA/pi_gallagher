"""
P.I. Gallagher: The Missing Art

IntroSubstate — Narrative introduction for the Police Archive minigame.
Displays typewriter-effect text setting the scene for Lauren's infiltration.
"""

import pygame

from gale.state import BaseState
from gale.input_handler import InputData
from gale.text import render_text

import settings
from src.data.archive_data import COLORS, INTRO_TEXT


class IntroSubstate(BaseState):
    def __init__(self, state_machine, parent_state):
        super().__init__(state_machine)
        self.parent = parent_state

    def enter(self, **kwargs):
        self.full_text = INTRO_TEXT
        self.char_index = 0
        self.total_chars = len(self.full_text)
        self.char_timer = 0.0
        self.CHAR_SPEED = 0.035
        self.finished_typing = False
        self.alpha = 0.0

    def update(self, dt):
        # Fade in
        if self.alpha < 255:
            self.alpha = min(255, self.alpha + 200 * dt)

        # Typewriter effect
        if not self.finished_typing:
            self.char_timer += dt
            while (
                self.char_timer >= self.CHAR_SPEED
                and self.char_index < self.total_chars
            ):
                self.char_timer -= self.CHAR_SPEED
                self.char_index += 1
            if self.char_index >= self.total_chars:
                self.finished_typing = True

    def on_input(self, input_id, input_data):
        if input_id == "space" and input_data.pressed:
            if not self.finished_typing:
                self.char_index = self.total_chars
                self.finished_typing = True
            else:
                self.state_machine.change("phase_a")

    def render(self, surface):
        surface.fill(COLORS["background"])

        # Title
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

        # Subtitle
        render_text(
            surface,
            "— Sótano —",
            settings.FONTS["medium"],
            settings.VIRTUAL_WIDTH // 2,
            42,
            COLORS["muted"],
            center=True,
        )

        # Narrative text with typewriter effect
        visible_text = self.full_text[: self.char_index]
        visible_lines = visible_text.split("\n")

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

        # Prompt
        if self.finished_typing:
            render_text(
                surface,
                "ESPACIO para continuar",
                settings.FONTS["medium"],
                settings.VIRTUAL_WIDTH // 2,
                240,
                COLORS["muted"],
                center=True,
            )

        # Fade-in overlay
        if self.alpha < 255:
            overlay = pygame.Surface(
                (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA
            )
            overlay.fill((0, 0, 0, int(255 - self.alpha)))
            surface.blit(overlay, (0, 0))
