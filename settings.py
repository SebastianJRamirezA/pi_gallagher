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
from gale import tilemap

input_handler.InputHandler.set_keyboard_action(input_handler.KEY_ESCAPE, "quit")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_LEFT, "move_left")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_RIGHT, "move_right")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_UP, "move_up")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_DOWN, "move_down")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_SPACE, "interact")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_e, "interact")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_RETURN, "enter")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_KP_ENTER, "enter")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_c, "confirm")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_d, "details")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_i, "details")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_h, "hint")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_p, "pause")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_a, "rotate_left")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_LSHIFT, "fine")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_RSHIFT, "fine")

TITLE = "P.I. Gallagher: The Missing Art"

# Size of our actual window. The original creates a plain 320x200
# window with no virtual-resolution scaling, so window and virtual
# sizes match here too.
VIRTUAL_WIDTH = 480
VIRTUAL_HEIGHT = 270

# Size we are trying to emulate
WINDOW_WIDTH = VIRTUAL_WIDTH * 3
WINDOW_HEIGHT = VIRTUAL_HEIGHT * 3

FONTS = {
    "small": pygame.font.Font(None, 16),
    "medium": pygame.font.Font(None, 22),
    "large": pygame.font.Font(None, 34),
}

BASE_DIR = pathlib.Path(__file__).parent

TEXTURES = {
    "city_tiles": pygame.image.load(BASE_DIR / "assets" / "graphics" / "city_tileset.png"),
    "indoor_tiles": pygame.image.load(BASE_DIR / "assets" / "graphics" / "indoor_tileset.png"),
    "rpg_tiles": pygame.image.load(BASE_DIR / "assets" / "graphics" / "rpg_tileset.png"),
}


def _actor_sheet(color):
    sheet = pygame.Surface((48, 72), pygame.SRCALPHA)
    for index in range(12):
        x = (index % 3) * 16
        y = (index // 3) * 18
        pygame.draw.rect(sheet, color, (x + 4, y + 2, 8, 10))
        pygame.draw.rect(sheet, (30, 30, 30), (x + 3, y + 12, 10, 5))
    return sheet


TEXTURES["player"] = _actor_sheet((190, 205, 220))
TEXTURES["npc"] = _actor_sheet((210, 165, 105))
TEXTURES["gallagher"] = pygame.image.load(BASE_DIR / "assets" / "graphics" / "gallagher.png")

FRAMES = {
    "city_tiles": frames.generate_frames(TEXTURES["city_tiles"], 16, 16),
    "indoor_tiles": frames.generate_frames(TEXTURES["indoor_tiles"], 16, 16),
    "player": frames.generate_frames(TEXTURES["player"], 16, 18),
    "npc": frames.generate_frames(TEXTURES["npc"], 16, 18),
    "gallagher": frames.generate_frames(TEXTURES["gallagher"], 19, 28),
}

TILE_SIZE = 16
TILE_WIDTH = VIRTUAL_WIDTH // TILE_SIZE
TILE_HEIGHT = VIRTUAL_HEIGHT // TILE_SIZE
CAMERA_FOLLOW_RATE = 8.0
TILESET_IMAGES = {
    "rpg_tileset.tsj": TEXTURES["rpg_tiles"],
    "indoor_tileset.tsj": TEXTURES["indoor_tiles"],
    "city_tileset.tsj": TEXTURES["city_tiles"],
}
TILESETS = {
    "rpg_tileset.tsj": tilemap.Tileset(TEXTURES["rpg_tiles"], TILE_SIZE, TILE_SIZE, 1, spacing=1),
    "indoor_tileset.tsj": tilemap.Tileset(TEXTURES["indoor_tiles"], TILE_SIZE, TILE_SIZE, 1768, spacing=1),
    "city_tileset.tsj": tilemap.Tileset(TEXTURES["city_tiles"], TILE_SIZE, TILE_SIZE, 2254, spacing=1),
}

FONTS = {
    "small": pygame.font.Font(None, 14),
    "medium": pygame.font.Font(None, 18),
    "large": pygame.font.Font(None, 26),
    "xlarge": pygame.font.Font(None, 42),
}

SOUNDS = {
    "clock": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "clock.wav"),
}
