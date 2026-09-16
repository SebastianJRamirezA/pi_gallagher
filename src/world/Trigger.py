"""
P.I. Gallagher: The Missing Art

Trigger — Interactive zones on top-down maps for minigames, dialogues,
inspections, corkboard, and zone transitions with conditional gating.
"""

from typing import Any, Callable, Optional, Tuple

import pygame

from src.story.StoryManager import StoryManager


class Trigger:
    def __init__(
        self,
        trigger_id: str,
        x: float,
        y: float,
        width: float,
        height: float,
        trigger_type: str,
        prompt_text: str = "",
        target: Optional[str] = None,
        condition_fn: Optional[Callable[[StoryManager], Tuple[bool, str]]] = None,
        action_fn: Optional[Callable[[Any, StoryManager], None]] = None,
    ) -> None:
        self.trigger_id = trigger_id
        self.rect = pygame.Rect(round(x), round(y), round(width), round(height))
        self.trigger_type = trigger_type
        self.prompt_text = prompt_text
        self.target = target
        self.condition_fn = condition_fn
        self.action_fn = action_fn

    def collides(self, player_rect: pygame.Rect) -> bool:
        """Check if the player is touching or overlapping this trigger area."""
        # Expand trigger slightly for easy interaction proximity (6px margin)
        expanded = self.rect.inflate(12, 12)
        return player_rect.colliderect(expanded)

    def check_condition(self, story: StoryManager) -> Tuple[bool, str]:
        """Verify if this trigger's condition is met."""
        if self.condition_fn is not None:
            return self.condition_fn(story)
        return True, ""

