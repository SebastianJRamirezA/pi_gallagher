"""
ISPPV1 2023
Study Case: Hello World

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class that runs the whole game, showing the
most basic use of Gale: opening a window and drawing text on it.
"""

import pygame

from gale.game import Game
from gale.input_handler import InputData
from gale.text import render_text
from gale.state import StateStack

from src.states.StealthMinigameState import StealthMinigameState

import settings


class PiGallagher(Game):
    def init(self) -> None:
        self.state_machine = StateStack()
        self.state_machine.push(StealthMinigameState(self.state_machine))

    def update(self, dt: float) -> None:
        self.state_machine.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        self.state_machine.render(surface)

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "quit" and input_data.pressed:
            self.quit()
        else: 
            self.state_machine.on_input(input_id, input_data)