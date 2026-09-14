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
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_a, "rotate_left")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_LEFT, "rotate_left")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_d, "rotate_right")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_RIGHT, "rotate_right")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_LSHIFT, "fine")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_RSHIFT, "fine")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_SPACE, "confirm")

TITLE = "P.I. Gallagher: The Missing Art"

# Size of our actual window. The original creates a plain 320x200
# window with no virtual-resolution scaling, so window and virtual
# sizes match here too.
VIRTUAL_WIDTH = 480
VIRTUAL_HEIGHT = 270

# Size we are trying to emulate
WINDOW_WIDTH = 960
WINDOW_HEIGHT = 540

FONTS = {
    "small": pygame.font.Font(None, 16),
    "medium": pygame.font.Font(None, 22),
    "large": pygame.font.Font(None, 34),
}

COLOR_BACKGROUND = (18, 20, 24)
COLOR_PANEL = (31, 33, 38)
COLOR_BRASS = (190, 147, 73)
COLOR_STEEL = (116, 124, 132)
COLOR_TEXT = (218, 214, 198)
COLOR_MUTED = (119, 125, 130)
COLOR_DANGER = (196, 72, 57)
COLOR_SUCCESS = (105, 173, 116)

DIAL_SPEED = 72.0
FINE_DIAL_SPEED = 18.0
COMBINATION = (32, 74, 18)


BASE_DIR = pathlib.Path(__file__).parent

TEXTURES = {
    "city_tiles": pygame.image.load(BASE_DIR / "assets" / "graphics" / "city_tileset.png"),
    "indoor_tiles": pygame.image.load(BASE_DIR / "assets" / "graphics" / "indoor_tileset.png"),
}

FRAMES = {
    "city_tiles": frames.generate_frames(TEXTURES["city_tiles"], 16, 16),
    "indoor_tiles": frames.generate_frames(TEXTURES["indoor_tiles"], 16, 16),
}
