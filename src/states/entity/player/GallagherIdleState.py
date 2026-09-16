"""
P.I. Gallagher: The Missing Art

GallagherIdleState — Player is standing still.
Switches to 'walk' as soon as any movement key is held.
"""

import pygame

from src.states.entity.BaseEntityState import BaseEntityState


class GallagherIdleState(BaseEntityState):
    def enter(self, **kwargs) -> None:
        self.entity.change_animation(f"idle-{self.entity.direction}")

    def update(self, dt: float) -> None:
        held = self.entity.held
        if (
            held["move_left"]
            or held["move_right"]
            or held["move_up"]
            or held["move_down"]
        ):
            self.entity.change_state("walk")

    def render(self, surface: pygame.Surface) -> None:
        anim = self.entity.current_animation
        self.entity.render_sprite(surface, anim.get_current_frame())

