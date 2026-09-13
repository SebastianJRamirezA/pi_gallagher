"""
P.I. Gallagher: The Missing Art

This file contains the game settings that include the association of the
inputs with an their ids, constants of values to set up the game, and
fonts.
"""

import pathlib

import pygame

from gale import frames
from gale import input_handler

input_handler.InputHandler.set_keyboard_action(input_handler.KEY_ESCAPE, "quit")

TITLE = "P.I. Gallagher: The Missing Art"

# Size of our actual window. The original creates a plain 320x200
# window with no virtual-resolution scaling, so window and virtual
# sizes match here too.
VIRTUAL_WIDTH = 400
VIRTUAL_HEIGHT = 192

# Size we are trying to emulate
WINDOW_WIDTH = VIRTUAL_WIDTH * 4
WINDOW_HEIGHT = VIRTUAL_HEIGHT * 4


BASE_DIR = pathlib.Path(__file__).parent

TEXTURES = {
    "city_tiles": pygame.image.load(BASE_DIR / "assets" / "graphics" / "city_tileset.png"),
    "indoor_tiles": pygame.image.load(BASE_DIR / "assets" / "graphics" / "indoor_tileset.png"),
}

FRAMES = {
    "city_tiles": frames.generate_frames(TEXTURES["city_tiles"], 16, 16),
    "indoor_tiles": frames.generate_frames(TEXTURES["indoor_tiles"], 16, 16),
}
