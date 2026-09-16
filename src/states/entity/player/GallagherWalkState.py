"""
P.I. Gallagher: The Missing Art

GallagherWalkState — Player is walking.
Updates direction and walk animation based on held movement keys.
Switches back to 'idle' when no movement key is held.
"""

import pygame

from src.states.entity.BaseEntityState import BaseEntityState


class GallagherWalkState(BaseEntityState):
    def enter(self, **kwargs) -> None:
        self.entity.change_animation(f"walk-{self.entity.direction}")

    def update(self, dt: float) -> None:
        player = self.entity
        held = player.held

        if held["move_left"]:
            player.direction = "left"
            player.change_animation("walk-left")
        elif held["move_right"]:
            player.direction = "right"
            player.change_animation("walk-right")
        elif held["move_up"]:
            player.direction = "up"
            player.change_animation("walk-up")
        elif held["move_down"]:
            player.direction = "down"
            player.change_animation("walk-down")
        else:
            player.change_state("idle")

    def render(self, surface: pygame.Surface) -> None:
        anim = self.entity.current_animation
        self.entity.render_sprite(surface, anim.get_current_frame())

