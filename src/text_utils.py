"""
P.I. Gallagher: The Missing Art

Author: Alejandro Mujica
Snippet taken from ISPPV1 2023 - Study Case: Ultimate Fantasy (RPG)

This file contains wrap_text, a small greedy word-wrap helper shared by
every screen that renders a paragraph too long for one line (see
TheEndState, ConfirmState) -- a single unbroken font.render(text, ...)
has no notion of the surface it'll end up on, so a long enough paragraph
would otherwise run straight off the screen's edge.
"""

from typing import List

import pygame


def wrap_text(font: pygame.font.Font, text: str, max_width: float) -> List[str]:
    """Greedily packs words into as few lines as possible, each rendering
    no wider than max_width."""
    words = text.split(" ")
    lines: List[str] = []
    current = ""

    for word in words:
        candidate = f"{current} {word}".strip()

        if current and font.size(candidate)[0] > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate

    if current:
        lines.append(current)

    return lines

class TypewriterEffect:
    """Helper class to manage typewriter text revelation animations."""

    def __init__(self, char_speed: float = 0.035) -> None:
        self.char_speed = char_speed
        self.full_text = ""
        self.char_index = 0
        self.char_timer = 0.0
        self.finished = True

    def set_text(self, text: str) -> None:
        """Resets state with new text to animate."""
        self.full_text = text
        self.char_index = 0
        self.char_timer = 0.0
        self.finished = len(text) == 0

    def update(self, dt: float) -> None:
        """Advances character counter based on delta time."""
        if self.finished:
            return

        self.char_timer += dt
        total_chars = len(self.full_text)
        
        while self.char_timer >= self.char_speed and self.char_index < total_chars:
            self.char_timer -= self.char_speed
            self.char_index += 1

        if self.char_index >= total_chars:
            self.finished = True

    def complete(self) -> None:
        """Instantly finishes typing out the text."""
        self.char_index = len(self.full_text)
        self.finished = True

    @property
    def visible_text(self) -> str:
        """Returns the slice of text that should currently be rendered."""
        return self.full_text[: self.char_index]
