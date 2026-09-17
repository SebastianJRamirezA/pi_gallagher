"""
P.I. Gallagher: The Missing Art

SuccessSubstate — Victory screen for the Police Archive minigame.
Displays collected clues and narrative conclusion.
"""

import pygame

from gale.state import BaseState
from gale.input_handler import InputData
from gale.text import render_text
from gale.timer import Timer

import settings
from src.data.archive_data import COLORS, CLUES, SUCCESS_TEXT


class SuccessSubstate(BaseState):
    def __init__(self, state_machine, parent_state):
        super().__init__(state_machine)
        self.parent = parent_state

    def enter(self, **kwargs):
        self.alpha = 0.0
        from src.story.StoryManager import StoryManager
        story = StoryManager.get_instance()
        for c in ("C02", "C03", "C12"):
            story.add_card(c)
        story.flags["archive_completed"] = True

    def update(self, dt):
        if self.alpha < 255:
            self.alpha = min(255, self.alpha + 150 * dt)

    def on_input(self, input_id, input_data):
        if input_data.pressed and input_id in {"confirm", "enter", "interact"}:
            # if getattr(self.parent, "door", None) is not None:
            #     self.parent.door.active = True
            self.parent.state_machine.pop()

    def render(self, surface):
        surface.fill(COLORS["background"])

        # Title
        render_text(
            surface,
            "MISIÓN COMPLETADA",
            settings.FONTS["large"],
            settings.VIRTUAL_WIDTH // 2,
            15,
            COLORS["success"],
            center=True,
            shadowed=True,
        )

        # Show collected clues
        y = 55
        for clue_id in self.parent.collected_clues:
            clue = CLUES.get(clue_id)
            if clue is None:
                continue

            # Clue card background
            card_rect = pygame.Rect(60, y - 4, 360, 42)
            pygame.draw.rect(surface, COLORS["panel"], card_rect, border_radius=3)
            pygame.draw.rect(
                surface, COLORS["brass_dark"], card_rect, 1, border_radius=3
            )

            render_text(
                surface,
                f"[{clue['id']}] {clue['titulo']}",
                settings.FONTS["small"],
                card_rect.x + 10,
                y + 2,
                COLORS["brass"],
            )
            keywords_text = ", ".join(clue["claves"])
            render_text(
                surface,
                f"Claves: {keywords_text}",
                settings.FONTS["small"],
                card_rect.x + 10,
                y + 20,
                COLORS["highlight"],
            )
            y += 50

        # Narrative conclusion
        lines = SUCCESS_TEXT.split("\n")
        y = max(y + 5, 210)
        for line in lines:
            if line:
                render_text(
                    surface,
                    line,
                    settings.FONTS["small"],
                    settings.VIRTUAL_WIDTH // 2,
                    y,
                    COLORS["paper"],
                    center=True,
                )
            y += 16

        # Fade-in overlay
        if self.alpha < 255:
            overlay = pygame.Surface(
                (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA
            )
            overlay.fill((0, 0, 0, int(255 - self.alpha)))
            surface.blit(overlay, (0, 0))
