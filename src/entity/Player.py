from typing import Any, Dict

import pygame

from gale.animation import Animation
from gale.state import StateMachine

import settings
from src.entity.Actor import Actor
from src.definitions.gallagher import GALLAGHER_DEFS


class Player(Actor):
    """
    Player character driven by a per-entity StateMachine (idle / walk).
    Movement physics (collision) stays in World; states handle direction,
    animation selection, and state transitions.
    """

    SPEED = 92.0

    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, "gallagher", "Tim Gallagher")
        self.held = {
            "move_left": False,
            "move_right": False,
            "move_up": False,
            "move_down": False,
        }

        # Animation system (same pattern as 06_princess Entity)
        self.animations = _create_animations(GALLAGHER_DEFS["animations"])
        self.current_animation = None

        # Camera reference set by World before render
        self.camera = None

        # Cache for flipped surfaces when facing left
        self._flipped_frames: Dict[int, pygame.Surface] = {}

        # Entity state machine (lazy imports avoid circular dependencies)
        from src.states.entity.player.GallagherIdleState import GallagherIdleState
        from src.states.entity.player.GallagherWalkState import GallagherWalkState

        self.state_machine = StateMachine(
            {
                "idle": lambda sm: GallagherIdleState(self, sm),
                "walk": lambda sm: GallagherWalkState(self, sm),
            }
        )
        self.state_machine.change("idle")

    # ── Collision / Geometry ────────────────────────────────────────────

    @property
    def rect(self) -> pygame.Rect:
        """Full 20x33 sprite bounds — matches what is rendered and is used for interaction detection."""
        return pygame.Rect(round(self.x), round(self.y), 20, 33)

    @property
    def collision_rect(self) -> pygame.Rect:
        """13x14 foot-box used exclusively for tile walkability and door collision."""
        return pygame.Rect(round(self.x + 4), round(self.y + 15), 13, 14)

    # ── State / animation helpers ──────────────────────────────────────

    def change_state(self, name: str) -> None:
        self.state_machine.change(name)

    def change_animation(self, name: str) -> None:
        if self.current_animation != self.animations.get(name):
            self.current_animation = self.animations[name]
            self.current_animation.reset()

    # ── Update ─────────────────────────────────────────────────────────

    def update(self, dt: float) -> None:
        self.state_machine.update(dt)
        if self.current_animation:
            self.current_animation.update(dt)

    # ── Render ─────────────────────────────────────────────────────────

    def render_sprite(self, surface: pygame.Surface, frame_index: int) -> None:
        """Draw the current animation frame, applying camera transform and flipping if facing left."""
        texture = settings.TEXTURES[self.texture]
        frame = settings.FRAMES[self.texture][frame_index]
        pos = pygame.Rect(round(self.x), round(self.y), frame.width, frame.height)
        if self.camera is not None:
            pos = self.camera.apply(pos)

        if self.direction == "left":
            if frame_index not in self._flipped_frames:
                self._flipped_frames[frame_index] = pygame.transform.flip(
                    texture.subsurface(frame), True, False
                )
            surface.blit(self._flipped_frames[frame_index], pos)
        else:
            surface.blit(texture, pos, frame)

    def render(self, surface: pygame.Surface, camera: Any = None) -> None:
        self.camera = camera
        self.state_machine.render(surface)

    # ── Input ──────────────────────────────────────────────────────────

    def on_input(self, input_id: str, input_data: Any) -> None:
        if input_id in self.held:
            self.held[input_id] = input_data.pressed or not input_data.released


def _create_animations(
    animation_defs: Dict[str, Dict[str, Any]],
) -> Dict[str, Animation]:
    """Build Animation objects from a definitions dict (same format as 06_princess)."""
    animations = {}
    for name, defn in animation_defs.items():
        anim = Animation(
            defn["frames"],
            defn.get("interval", 0),
            loops=defn.get("loops"),
        )
        anim.texture_id = defn.get("texture", "gallagher")
        animations[name] = anim
    return animations

