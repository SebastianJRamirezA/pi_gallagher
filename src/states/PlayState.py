from typing import Any

import pygame
from gale.state import BaseState

import settings
from src.world.World import World


class PlayState(BaseState):
    def enter(self) -> None:
        self.world = World(self.state_machine)

    def update(self, dt: float) -> None:
        self.world.update(dt)

    def on_input(self, input_id: str, input_data: Any) -> None:
        if input_id == "pause" and input_data.pressed:
            self.world._clear_movement()
            self.state_machine.push(PauseMenuState(self.state_machine))
            return
        self.world.on_input(input_id, input_data)

    def render(self, surface: pygame.Surface) -> None:
        self.world.render(surface)
        label = settings.FONTS["small"].render(self.world.current_region_name.upper(), True, (255, 255, 255))
        surface.blit(label, (8, 8))


from src.states.PauseMenuState import PauseMenuState
