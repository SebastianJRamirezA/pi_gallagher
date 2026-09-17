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


def test_minigame_completion_prevents_reaccess():
    from src.story.StoryManager import StoryManager

    story = StoryManager.get_instance()
    story.reset()

    # Before talking to Sofia: locked
    allowed, reason = story.can_access_minigame("stealth")
    assert not allowed
    assert "Sofia" in reason

    # After talking to Sofia: accessible
    story.flags["sofia_club_talked"] = True
    allowed, reason = story.can_access_minigame("stealth")
    assert allowed
    assert reason == ""

    # Once completed: permanently locked with narrative explanation
    story.flags["stealth_completed"] = True
    allowed, reason = story.can_access_minigame("stealth")
    assert not allowed
    assert "oficinas traseras" in reason

    # Archive completion gating
    story.flags["archive_completed"] = True
    allowed, reason = story.can_access_minigame("archive")
    assert not allowed
    assert "archivos policiales" in reason

    # Safecracker completion gating
    story.flags["safecracker_completed"] = True
    allowed, reason = story.can_access_minigame("safecracker")
    assert not allowed
    assert "caja fuerte" in reason


def test_stealth_minigame_finishes_and_repositions_player():
    from src.states.StealthMinigameState import StealthMinigameState
    from src.story.StoryManager import StoryManager
    from src.states.PlayState import PlayState

    story = StoryManager.get_instance()
    story.reset()
    story.flags["sofia_office_talked"] = True
    story.flags["sofia_club_talked"] = True

    stack = StateStack()
    play_state = PlayState(stack)
    stack.push(play_state)

    world = play_state.world
    world.current_region_name = "nightclub"
    world.player.x = 390
    world.player.y = 8  # Inside the stealth door hitbox

    # Entering stealth repositions player y outside the door hitbox
    world._try_enter_club_door("stealth")
    assert len(stack.states) == 2
    assert isinstance(stack.states[-1], StealthMinigameState)
    assert world.player.y >= 52

    stealth_state = stack.states[-1]
    # Move player directly onto the goal in the minigame
    stealth_state.player.topleft = stealth_state.goal.topleft

    # Update runs _check_goal
    stealth_state.update(0.016)

    # Stealth state should have popped from the stack
    assert len(stack.states) == 1
    assert stack.states[-1] is play_state

    # Clues C09 and C11 must be added and stealth marked as completed
    assert story.flags["stealth_completed"] is True
    assert story.has_card("C09")
    assert story.has_card("C11")

    # Player position in world is outside the door hitbox
    assert world.player.y >= 52

    # Attempting to enter again should be denied and player pushed back
    prev_y = world.player.y
    world._try_enter_club_door("stealth")
    assert len(stack.states) == 2  # Pushes monologue DialogueState, NOT StealthMinigameState
    assert not isinstance(stack.states[-1], StealthMinigameState)
    assert world.player.y == prev_y + 14


import unittest


class TestWorldMinigames(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        if pygame.display.get_surface() is None:
            pygame.display.set_mode((1, 1))

    def test_mapping(self):
        test_world_minigame_mapping_is_defined()

    def test_collision(self):
        test_world_detects_minigame_collision_by_name()

    def test_completion_gating(self):
        test_minigame_completion_prevents_reaccess()

    def test_stealth_exit_and_reposition(self):
        test_stealth_minigame_finishes_and_repositions_player()


