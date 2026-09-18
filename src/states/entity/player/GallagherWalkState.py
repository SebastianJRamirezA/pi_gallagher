"""
P.I. Gallagher: The Missing Art

GallagherWalkState — Player is walking.
Updates direction and walk animation based on held movement keys.
Switches back to 'idle' when no movement key is held.
Plays sequential footstep audio clips while walking.
"""

import pygame

import settings
from src.states.entity.BaseEntityState import BaseEntityState


class GallagherWalkState(BaseEntityState):
    STEP_INTERVAL = 0.25  # Time in seconds between footsteps

    def __init__(self, entity, state_machine=None) -> None:
        super().__init__(entity, state_machine)
        self.footstep_index = 0
        self.footstep_timer = 0.0

    def play_footstep(self) -> None:
        sound_key = f"footstep{self.footstep_index:02d}"
        if sound_key in settings.SOUNDS:
            settings.SOUNDS[sound_key].play()
        self.footstep_index = (self.footstep_index + 1) % 10

    def enter(self, **kwargs) -> None:
        self.entity.change_animation(f"walk-{self.entity.direction}")
        
        # Reset and play the first step immediately
        self.footstep_index = 0
        self.footstep_timer = 0.0
        self.play_footstep()

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
            return

        # Advance audio timer for subsequent footsteps
        self.footstep_timer += dt
        if self.footstep_timer >= self.STEP_INTERVAL:
            self.footstep_timer = 0.0
            self.play_footstep()

    def render(self, surface: pygame.Surface) -> None:
        anim = self.entity.current_animation
        self.entity.render_sprite(surface, anim.get_current_frame())