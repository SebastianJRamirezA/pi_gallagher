"""
P.I. Gallagher: The Missing Art

Stealth Minigame State — top-down stealth prototype.

The detective must cross a guarded area without being spotted.
Guards have a directional cone of vision that is blocked by obstacles.
Detection resets the player to the starting position.
"""

import math
from typing import List, Dict, Tuple, Optional

import pygame

from gale.state import BaseState
from gale.camera import Camera
from gale.input_handler import InputData

import settings

def _segments_from_rect(rect: pygame.Rect) -> List[Tuple[Tuple[float, float], Tuple[float, float]]]:
    """Return the four edge segments of a rectangle."""
    l, t, r, b = rect.left, rect.top, rect.right, rect.bottom
    return [
        ((l, t), (r, t)),  # top
        ((r, t), (r, b)),  # right
        ((r, b), (l, b)),  # bottom
        ((l, b), (l, t)),  # left
    ]


def _segment_intersects(
    p: Tuple[float, float],
    q: Tuple[float, float],
    a: Tuple[float, float],
    b: Tuple[float, float],
) -> bool:
    """
    Return True when segment PQ intersects segment AB.
    Uses the standard parametric cross-product test — O(1) per pair.
    Only considers intersections strictly between the endpoints
    (t in (0,1) and u in (0,1)) so that touching a corner shared by
    guard and obstacle does not count as a block.
    """
    dx, dy = q[0] - p[0], q[1] - p[1]
    sx, sy = b[0] - a[0], b[1] - a[1]

    denom = dx * sy - dy * sx
    if abs(denom) < 1e-9:
        return False

    ax_, ay_ = a[0] - p[0], a[1] - p[1]
    t = (ax_ * sy - ay_ * sx) / denom
    u = (ax_ * dy - ay_ * dx) / denom

    return 0.0 < t < 1.0 and 0.0 < u < 1.0


def line_of_sight_blocked(
    origin: Tuple[float, float],
    target: Tuple[float, float],
    obstacles: List[pygame.Rect],
) -> bool:
    """Return True when any obstacle edge intersects the segment origin→target."""
    for obs in obstacles:
        for seg_a, seg_b in _segments_from_rect(obs):
            if _segment_intersects(origin, target, seg_a, seg_b):
                return True
    return False

def _make_guard(
    x: float, y: float, w: float, h: float,
    angle: float, fov: float, distance: float,
    patrol: Optional[List[Dict]] = None,
) -> Dict:
    """
    Build a guard dict.

    angle    – direction the guard faces, in degrees.
               0° = right, 90° = down (pygame screen coords), etc.
    fov      – total cone aperture in degrees.
    distance – how far the cone reaches (in world pixels).
    patrol   – optional list of waypoints: [{"x", "y", "angle"}, ...]
    """
    guard = {
        "rect": pygame.Rect(x, y, w, h),
        "fx": float(x),
        "fy": float(y),
        "angle": angle,
        "fov": fov,
        "distance": distance,
        "patrol": patrol,
        "patrol_index": 0,
        "patrol_speed": 40,
    }
    return guard

class StealthMinigameState(BaseState):
    """
    Self-contained stealth minigame driven by Gale's BaseState lifecycle.

    enter()  → sets up world data (player, obstacles, guards, camera).
    update() → polls keyboard, moves player, runs guard patrols & detection.
    render() → draws everything through the camera offset.
    """

    def enter(self, **enter_params) -> None:
        self.vw: int = settings.VIRTUAL_WIDTH  
        self.vh: int = settings.VIRTUAL_HEIGHT  

        self.world_width: int = 800
        self.world_height: int = 400

        self.camera = Camera(self.vw, self.vh, bounds=pygame.Rect(0, 0, self.world_width, self.world_height))

        self.player_spawn = (24, 24)
        self.player = pygame.Rect(self.player_spawn[0], self.player_spawn[1], 8, 8)
        self.player_speed_x: float = 0.0
        self.player_speed_y: float = 0.0

        self.goal = pygame.Rect(self.world_width - 40, self.world_height - 30, 30, 20)

        self.detected_timer: float = 0.0
        self.completed: bool = False

        self._build_obstacles()
        self._build_guards()

    def _build_obstacles(self) -> None:
        """Static cover objects the player can hide behind."""
        self.obstacles: List[pygame.Rect] = [
            # Room 1 — starting area
            pygame.Rect(70, 30, 40, 10),
            pygame.Rect(70, 30, 10, 60),
            pygame.Rect(140, 80, 50, 10),
            pygame.Rect(30, 130, 10, 50),

            # Corridor
            pygame.Rect(200, 0, 10, 70),
            pygame.Rect(200, 110, 10, 90),
            pygame.Rect(260, 50, 10, 60),

            # Room 2 — central hall
            pygame.Rect(320, 20, 60, 10),
            pygame.Rect(350, 90, 10, 50),
            pygame.Rect(420, 60, 10, 80),
            pygame.Rect(300, 160, 80, 10),

            # Room 3 — approach to goal
            pygame.Rect(500, 30, 50, 10),
            pygame.Rect(550, 30, 10, 80),
            pygame.Rect(500, 140, 10, 60),
            pygame.Rect(600, 100, 60, 10),
            pygame.Rect(640, 180, 10, 50),

            # Far room
            pygame.Rect(700, 50, 50, 10),
            pygame.Rect(700, 130, 10, 70),

            # World border walls (keep the player in-bounds)
            pygame.Rect(0, 0, self.world_width, 2),           # top
            pygame.Rect(0, self.world_height - 2, self.world_width, 2),  # bottom
            pygame.Rect(0, 0, 2, self.world_height),           # left
            pygame.Rect(self.world_width - 2, 0, 2, self.world_height),  # right
        ]

    def _build_guards(self) -> None:
        """Guards: some static, some patrolling."""
        self.guards: List[Dict] = [
            # Guard 1 — static, watches corridor entrance
            _make_guard(180, 85, 10, 10, angle=180, fov=70, distance=80),

            # Guard 2 — patrols vertically in the corridor
            _make_guard(230, 75, 10, 10, angle=90, fov=60, distance=70,
                        patrol=[
                            {"x": 230, "y": 75, "angle": 90},
                            {"x": 230, "y": 150, "angle": 90},
                            {"x": 230, "y": 75, "angle": 270},
                        ]),

            # Guard 3 — static in central hall, faces left
            _make_guard(400, 40, 10, 10, angle=180, fov=80, distance=90),

            # Guard 4 — patrols horizontally in central hall
            _make_guard(310, 130, 10, 10, angle=0, fov=65, distance=75,
                        patrol=[
                            {"x": 310, "y": 130, "angle": 0},
                            {"x": 400, "y": 130, "angle": 0},
                            {"x": 310, "y": 130, "angle": 180},
                        ]),

            # Guard 5 — watches approach to goal
            _make_guard(580, 120, 10, 10, angle=90, fov=75, distance=80),

            # Guard 6 — patrols near the goal
            _make_guard(700, 100, 10, 10, angle=180, fov=70, distance=85,
                        patrol=[
                            {"x": 700, "y": 100, "angle": 180},
                            {"x": 700, "y": 200, "angle": 90},
                            {"x": 700, "y": 100, "angle": 270},
                        ]),
        ]

    def update(self, dt: float) -> None:
        if getattr(self, "completed", False):
            return
        self._update_player(dt)
        self._update_guards(dt)
        self._check_detection()
        if self._check_goal():
            return
        self._update_camera(dt)

        if self.detected_timer > 0:
            self.detected_timer -= dt

    def on_input(self, input_id, input_data):
        if input_id == "move_up":
            if input_data.pressed: 
                self.player_speed_y = -60.0
            elif input_data.released: 
                self.player_speed_y = 0.0
        elif input_id == "move_down":
            if input_data.pressed: 
                self.player_speed_y = 60.0
            elif input_data.released: 
                self.player_speed_y = 0.0
        elif input_id == "move_right":
            if input_data.pressed: 
                self.player_speed_x = 60.0
            elif input_data.released: 
                self.player_speed_x = 0.0
        elif input_id == "move_left":
            if input_data.pressed: 
                self.player_speed_x = -60.0
            elif input_data.released: 
                self.player_speed_x = 0.0

    def _update_player(self, dt):
        self.player.x += self.player_speed_x * dt

        for obs in self.obstacles:
            if self.player.colliderect(obs):
                if self.player_speed_x > 0:
                    self.player.right = obs.left
                elif self.player_speed_x < 0:
                    self.player.left = obs.right

        self.player.y += self.player_speed_y * dt 

        for obs in self.obstacles:
            if self.player.colliderect(obs):
                if self.player_speed_y > 0:
                    self.player.bottom = obs.top
                elif self.player_speed_y < 0:
                    self.player.top = obs.bottom

    def _update_guards(self, dt: float) -> None:
        for guard in self.guards:
            patrol = guard["patrol"]
            if patrol is None:
                continue

            wp = patrol[guard["patrol_index"]]
            tx, ty = float(wp["x"]), float(wp["y"])
            gx, gy = guard["fx"], guard["fy"]

            dist = math.hypot(tx - gx, ty - gy)
            if dist < 1.0:
                # Snap to waypoint, adopt its facing angle
                guard["fx"] = tx
                guard["fy"] = ty
                guard["angle"] = wp["angle"]
                guard["patrol_index"] = (
                    (guard["patrol_index"] + 1) % len(patrol)
                )
            else:
                # Move toward waypoint (float precision)
                speed = guard["patrol_speed"] * dt
                ratio = min(speed / dist, 1.0)
                guard["fx"] += (tx - gx) * ratio
                guard["fy"] += (ty - gy) * ratio

                # Face movement direction while walking
                guard["angle"] = math.degrees(math.atan2(ty - gy, tx - gx))

            # Sync the integer Rect from the float position
            guard["rect"].x = int(guard["fx"])
            guard["rect"].y = int(guard["fy"])

    def _check_detection(self) -> None:
        px, py = self.player.center

        for guard in self.guards:
            gx, gy = guard["rect"].center

            # 1. Distance check
            dist = math.hypot(px - gx, py - gy)
            if dist > guard["distance"] or dist == 0:
                continue

            # 2. Angle check — is the player inside the cone?
            #    guard["angle"] uses screen-space convention:
            #    0° = right, 90° = down
            vx, vy = px - gx, py - gy
            rad = math.radians(guard["angle"])
            fx, fy = math.cos(rad), math.sin(rad)

            dot = vx * fx + vy * fy
            cos_to_player = dot / dist
            cos_to_player = max(-1.0, min(1.0, cos_to_player))
            angle_diff = math.degrees(math.acos(cos_to_player))

            if angle_diff > guard["fov"] / 2.0:
                continue

            # 3. Line-of-sight — is an obstacle between guard and player?
            if line_of_sight_blocked((gx, gy), (px, py), self.obstacles):
                continue

            # Detected!
            print("¡Detective descubierto! Reiniciando posición...")
            self._reset_player()
            break

    def _check_goal(self) -> bool:
        if getattr(self, "completed", False):
            return True
        if self.player.colliderect(self.goal):
            self.completed = True
            print("¡Objetivo alcanzado! El detective ha cruzado sin ser visto.")
            from src.story.StoryManager import StoryManager
            story = StoryManager.get_instance()
            for c in ("C09", "C11"):
                story.add_card(c)
            story.flags["stealth_completed"] = True
            if hasattr(self.state_machine, "states") and self.state_machine.states:
                for state in reversed(self.state_machine.states):
                    world = getattr(state, "world", None)
                    if world is not None and hasattr(world, "player"):
                        world.player.y = max(world.player.y, 52)
                        break
            self.state_machine.pop()
            return True
        return False

    def _reset_player(self) -> None:
        self.player.x = self.player_spawn[0]
        self.player.y = self.player_spawn[1]
        self.detected_timer = 0.6

    def _update_camera(self, dt: float) -> None:
        self.camera.x = self.player.centerx
        self.camera.y = self.player.centery
        self.camera.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((12, 10, 18))  # dark noir background

        cam = self.camera

        # 1. Goal zone (subtle green glow)
        goal_screen = cam.apply(self.goal)
        goal_surf = pygame.Surface((goal_screen.w, goal_screen.h), pygame.SRCALPHA)
        goal_surf.fill((40, 180, 80, 60))
        surface.blit(goal_surf, goal_screen.topleft)
        pygame.draw.rect(surface, (40, 180, 80), goal_screen, 1)

        # 2. Obstacles (dark grey bricks)
        for obs in self.obstacles:
            screen_rect = cam.apply(obs)
            pygame.draw.rect(surface, (55, 50, 60), screen_rect)
            pygame.draw.rect(surface, (75, 70, 80), screen_rect, 1)

        # 3. Guard FOV cones (translucent yellow)
        for guard in self.guards:
            self._render_fov(surface, guard, cam)

        # 4. Guards (red squares)
        for guard in self.guards:
            screen_guard = cam.apply(guard["rect"])
            pygame.draw.rect(surface, (190, 45, 45), screen_guard)
            pygame.draw.rect(surface, (220, 80, 80), screen_guard, 1)

        # 5. Player (blue circle)
        px, py = cam.world_to_screen(self.player.center)
        radius = max(int(self.player.w * cam.zoom / 2), 2)
        pygame.draw.circle(surface, (50, 100, 200), (int(px), int(py)), radius)
        pygame.draw.circle(surface, (100, 160, 255), (int(px), int(py)), radius, 1)

        # 6. Detection flash overlay
        if self.detected_timer > 0:
            alpha = int(120 * (self.detected_timer / 0.6))
            flash = pygame.Surface((self.vw, self.vh), pygame.SRCALPHA)
            flash.fill((200, 30, 30, alpha))
            surface.blit(flash, (0, 0))

    def _render_fov(
        self, surface: pygame.Surface, guard: Dict, cam: Camera
    ) -> None:
        """Draw a translucent cone polygon for the guard's field of view."""
        gx, gy = guard["rect"].center
        rad = math.radians(guard["angle"])
        half_fov = math.radians(guard["fov"] / 2.0)
        dist = guard["distance"]

        # Build cone arc as a fan of points (12 segments for smoothness)
        num_segments = 12
        world_points = [(gx, gy)]

        for i in range(num_segments + 1):
            frac = i / num_segments
            a = rad - half_fov + frac * (2 * half_fov)
            wx = gx + math.cos(a) * dist
            wy = gy + math.sin(a) * dist
            world_points.append((wx, wy))

        # Transform to screen
        screen_points = [cam.world_to_screen(p) for p in world_points]
        int_points = [(int(p[0]), int(p[1])) for p in screen_points]

        # Semi-transparent fill
        if len(int_points) >= 3:
            # Compute bounding box for the minimal surface
            xs = [p[0] for p in int_points]
            ys = [p[1] for p in int_points]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            w = max_x - min_x + 1
            h = max_y - min_y + 1

            if w > 0 and h > 0:
                fov_surf = pygame.Surface((w, h), pygame.SRCALPHA)
                shifted = [(p[0] - min_x, p[1] - min_y) for p in int_points]
                pygame.draw.polygon(fov_surf, (200, 190, 50, 35), shifted)
                pygame.draw.polygon(fov_surf, (200, 190, 50, 70), shifted, 1)
                surface.blit(fov_surf, (min_x, min_y))