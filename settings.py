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
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_SPACE, "space")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_e, "interact")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_f, "shoot")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_RETURN, "enter")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_KP_ENTER, "enter")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_d, "details")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_h, "hint")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_p, "pause")
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
TEXTURES["gallagher_shoot"] = pygame.image.load(BASE_DIR / "assets" / "graphics" / "gallagher_shot.png")
TEXTURES["bandit"] = pygame.image.load(BASE_DIR / "assets" / "graphics" / "bandit.png")
TEXTURES["bandit_hit"] = pygame.image.load(BASE_DIR / "assets" / "graphics" / "badit_hit.png")
TEXTURES["steiger"] = pygame.image.load(BASE_DIR / "assets" / "graphics" / "steiger.png")
TEXTURES["steiger_shot"] = pygame.image.load(BASE_DIR / "assets" / "graphics" / "steiger_shot.png")
TEXTURES["steiger_dash"] = pygame.image.load(BASE_DIR / "assets" / "graphics" / "steiger_dash.png")
TEXTURES["lauren"] = pygame.image.load(BASE_DIR / "assets" / "graphics" / "lauren.png")
TEXTURES["sofia"] = pygame.image.load(BASE_DIR / "assets" / "graphics" / "sofia.png")
TEXTURES["police"] = pygame.image.load(BASE_DIR / "assets" / "graphics" / "police.png")
TEXTURES["parroquiano"] = pygame.image.load(BASE_DIR / "assets" / "graphics" / "parroquiano.png")
TEXTURES["canillita"] = pygame.image.load(BASE_DIR / "assets" / "graphics" / "canillita.png")
TEXTURES["unemployed"] = pygame.image.load(BASE_DIR / "assets" / "graphics" / "unemployed.png")
TEXTURES["curador"] = pygame.image.load(BASE_DIR / "assets" / "graphics" / "curador.png")
TEXTURES["curator"] = TEXTURES["curador"]
TEXTURES["morales"] = pygame.image.load(BASE_DIR / "assets" / "graphics" / "morales.png")

FRAMES = {
    "city_tiles": frames.generate_frames(TEXTURES["city_tiles"], 16, 16),
    "indoor_tiles": frames.generate_frames(TEXTURES["indoor_tiles"], 16, 16),
    "player": frames.generate_frames(TEXTURES["player"], 16, 18),
    "npc": frames.generate_frames(TEXTURES["npc"], 16, 18),
    "gallagher": frames.generate_frames(TEXTURES["gallagher"], 19, 28),
    "gallagher_shoot": frames.generate_frames(TEXTURES["gallagher_shoot"], 20, 31),
    "bandit": frames.generate_frames(TEXTURES["bandit"], 20, 37),
    "bandit_hit": frames.generate_frames(TEXTURES["bandit_hit"], 30, 33),
    "steiger": frames.generate_frames(TEXTURES["steiger"], 20, 28),
    "steiger_shot": frames.generate_frames(TEXTURES["steiger_shot"], 20, 23),
    "steiger_dash": frames.generate_frames(TEXTURES["steiger_dash"], 20, 20),
    "lauren": frames.generate_frames(TEXTURES["lauren"], 12, 24),
    "sofia": frames.generate_frames(TEXTURES["sofia"], 12, 24),
    "police": frames.generate_frames(TEXTURES["police"], 15, 28),
    "parroquiano": frames.generate_frames(TEXTURES["parroquiano"], 15, 32),
    "canillita": frames.generate_frames(TEXTURES["canillita"], 15, 22),
    "unemployed": frames.generate_frames(TEXTURES["unemployed"], 15, 30),
    "curador": frames.generate_frames(TEXTURES["curador"], 15, 32),
    "curator": frames.generate_frames(TEXTURES["curador"], 15, 32),
    "morales": frames.generate_frames(TEXTURES["morales"], 15, 30),
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
    "doorClose_1": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "doorClose_1.ogg"),
    "doorClose_2": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "doorClose_2.ogg"),
    "doorClose_3": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "doorClose_3.ogg"),
    "doorClose_4": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "doorClose_4.ogg"),
    "doorOpen_1": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "doorOpen_1.ogg"),
    "doorOpen_2": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "doorOpen_2.ogg"),
    "footstep00": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "footstep00.ogg"),
    "footstep01": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "footstep01.ogg"),
    "footstep02": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "footstep02.ogg"),
    "footstep03": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "footstep03.ogg"),
    "footstep04": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "footstep04.ogg"),
    "footstep05": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "footstep05.ogg"),
    "footstep06": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "footstep06.ogg"),
    "footstep07": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "footstep07.ogg"),
    "footstep08": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "footstep08.ogg"),
    "footstep09": pygame.mixer.Sound(BASE_DIR / "assets" / "sounds" / "footstep09.ogg"),
}

for i in range(10):
    key = f"footstep{i:02d}"
    if key in SOUNDS:
        SOUNDS[key].set_volume(0.1)
