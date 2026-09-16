import pygame

from gale.state import StateStack

from src.world.World import World


def _make_door(name, x=0, y=0, width=20, height=20):
    return type(
        "Door",
        (),
        {"name": name, "x": x, "y": y, "width": width, "height": height},
    )()


def test_world_minigame_mapping_is_defined():
    assert set(World.MINIGAME_STATES) == {"stealth", "archive", "safecracker"}
    assert World.MINIGAME_STATES["stealth"].__name__ == "StealthMinigameState"


def test_world_detects_minigame_collision_by_name():
    stack = StateStack()
    world = World(stack)
    world.current_region_name = "nightclub"
    world.player.rect = pygame.Rect(0, 0, 14, 18)

    door = _make_door("stealth", 4, 4, 12, 12)

    assert world._door_collides_rect(world.player.rect, door)
    assert world._minigame_for_door(door) is World.MINIGAME_STATES["stealth"]
