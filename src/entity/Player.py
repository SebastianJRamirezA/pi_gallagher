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

    # ── State / animation helpers ──────────────────────────────────────

    def change_state(self, name: str) -> None:
        self.state_machine.change(name)

    def change_animation(self, name: str) -> None:
        self.current_animation = self.animations[name]

    # ── Update ─────────────────────────────────────────────────────────

    def update(self, dt: float) -> None:
        self.state_machine.update(dt)
        if self.current_animation:
            self.current_animation.update(dt)

    # ── Render ─────────────────────────────────────────────────────────

    def render_sprite(self, surface: pygame.Surface, frame_index: int) -> None:
        """Draw the current animation frame, applying camera transform."""
        texture = settings.TEXTURES[self.texture]
        frame = settings.FRAMES[self.texture][frame_index]
        pos = pygame.Rect(round(self.x), round(self.y), frame.width, frame.height)
        if self.camera is not None:
            pos = self.camera.apply(pos)
        surface.blit(texture, pos, frame)

    def render(self, surface: pygame.Surface, camera: Any = None) -> None:
        self.camera = camera
        self.state_machine.render(surface)
        # Draw collision box for debugging
        pygame.draw.rect(surface, (255, 0, 0), camera.apply(self.rect), 1)

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
