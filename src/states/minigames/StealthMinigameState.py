"""
P.I. Gallagher: The Missing Art

Stealth Minigame State — top-down stealth prototype with Actor integration and Noir aesthetic.
"""

import math
from typing import Any, List, Dict, Tuple, Optional

import pygame

from gale.state import BaseState
from gale.camera import Camera
from gale.timer import Timer
from gale.text import render_text
from gale.animation import Animation

from src.entity.Player import Player
from src.entity.Actor import Actor
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


class GuardActor(Actor):
    """Animated guard actor using the 100x60 guard spritesheet."""

    def __init__(
        self,
        x: float,
        y: float,
        texture: str = "guard",
        name: str = "Guardia",
        direction: str = "down",
    ) -> None:
        super().__init__(x, y, texture, name, direction=direction)
        # Fila 1: 2 sprites caminando hacia abajo (indices 0, 1)
        # Fila 2: 5 sprites caminando hacia la derecha (indices 5, 6, 7, 8, 9)
        # Fila 3: 2 sprites caminando hacia arriba (indices 10, 11)
        # Caminar a la izquierda: los mismos 5 sprites volteados
        self.animations: Dict[str, Animation] = {
            "down": Animation([0, 1], time_interval=0.25),
            "right": Animation([5, 6, 7, 8, 9], time_interval=0.12),
            "left": Animation([5, 6, 7, 8, 9], time_interval=0.12),
            "up": Animation([10, 11], time_interval=0.25),
        }
        self.current_animation = self.animations.get(self.direction, self.animations["down"])
        self.is_moving = False

    def update(self, dt: float, is_moving: bool = True) -> None:
        self.is_moving = is_moving
        target_anim = self.animations.get(self.direction, self.animations["down"])
        if self.current_animation != target_anim:
            self.current_animation = target_anim
            self.current_animation.reset()
        if self.is_moving:
            self.current_animation.update(dt)

    def render(self, surface: pygame.Surface, camera: Any = None) -> None:
        frame_idx = self.current_animation.get_current_frame()
        frame = settings.FRAMES[self.texture][frame_idx]
        texture = settings.TEXTURES[self.texture]
        image = pygame.Surface((frame.width, frame.height), pygame.SRCALPHA)
        image.blit(texture, (0, 0), frame)
        if self.direction == "left":
            image = pygame.transform.flip(image, True, False)
        # Centrar el sprite de 20x20 sobre el centro del hitbox (10x10)
        pos = pygame.Rect(round(self.x - 5), round(self.y - 5), frame.width, frame.height)
        if camera is not None:
            pos = camera.apply(pos)
        surface.blit(image, pos)


def _make_guard(
    x: float, y: float, w: float, h: float,
    angle: float, fov: float, distance: float,
    patrol: Optional[List[Dict]] = None,
    texture: str = "guard",
) -> Dict:
    """Build a guard dict with a GuardActor instance for visual rendering."""
    ang = angle % 360
    if 45 <= ang < 135:
        initial_dir = "down"
    elif 135 <= ang < 225:
        initial_dir = "left"
    elif 225 <= ang < 315:
        initial_dir = "up"
    else:
        initial_dir = "right"

    actor = GuardActor(x, y, texture, "Guardia", direction=initial_dir)
    guard = {
        "actor": actor,
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
    """

    def enter(self, **enter_params) -> None:
        # Load and play background stealth music endlessly
        music_path = settings.BASE_DIR / "assets" / "sounds" / "stealth.mp3"
        if music_path.exists():
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.play(loops=-1)

        self.vw: int = settings.VIRTUAL_WIDTH  
        self.vh: int = settings.VIRTUAL_HEIGHT  

        self.world_width: int = 800
        self.world_height: int = 220

        self.camera = Camera(self.vw, self.vh, bounds=pygame.Rect(0, 0, self.world_width, self.world_height))

        self.player_spawn = (24, 24)
        self.player_entity = Player(self.player_spawn[0], self.player_spawn[1])
        self.player_speed_x: float = 0.0
        self.player_speed_y: float = 0.0

        self.goal = pygame.Rect(self.world_width - 40, self.world_height - 50, 30, 40)

        self.detected_timer: float = 0.0
        self.completed: bool = False

        # Configuración del temporizador al igual que en SafeCrackerState
        self.timer = 45.0

        def decrement_timer():
            self.timer -= 1

            # Play warning sound on timer if we get low
            if self.timer <= 5 and self.timer > 0:
                if "clock" in settings.SOUNDS:
                    settings.SOUNDS["clock"].play()

        Timer.every(1, decrement_timer)

        self._build_obstacles()
        self._build_guards()

    def exit(self) -> None:
        """Stop background music when exiting this state."""
        pygame.mixer.music.fadeout(500)

    def _build_obstacles(self) -> None:
        """Static cover objects the player can hide behind."""
        self.obstacles: List[pygame.Rect] = [
            # Room 1 — starting area
            pygame.Rect(70, 20, 40, 10),
            pygame.Rect(70, 20, 10, 60),
            pygame.Rect(140, 70, 50, 10),
            pygame.Rect(30, 110, 10, 50),

            # Corridor
            pygame.Rect(200, 0, 10, 60),
            pygame.Rect(200, 100, 10, 80),
            pygame.Rect(260, 40, 10, 60),

            # Room 2 — central hall
            pygame.Rect(320, 20, 60, 10),
            pygame.Rect(350, 80, 10, 40),
            pygame.Rect(420, 50, 10, 70),
            pygame.Rect(300, 140, 80, 10),

            # Room 3 — approach to goal
            pygame.Rect(500, 20, 50, 10),
            pygame.Rect(550, 20, 10, 70),
            pygame.Rect(500, 120, 10, 50),
            pygame.Rect(600, 80, 60, 10),
            pygame.Rect(640, 130, 10, 50),

            # Far room
            pygame.Rect(700, 40, 50, 10),
            pygame.Rect(700, 110, 10, 60),

            # World border walls
            pygame.Rect(0, 0, self.world_width, 2),
            pygame.Rect(0, self.world_height - 2, self.world_width, 2),
            pygame.Rect(0, 0, 2, self.world_height),
            pygame.Rect(self.world_width - 2, 0, 2, self.world_height),
        ]

    def _build_guards(self) -> None:
        """Guards initialized with active patrols for maximum difficulty."""
        self.guards: List[Dict] = [
            # Guardia 1: Patrulla horizontal en la zona inicial
            _make_guard(180, 75, 10, 10, angle=180, fov=70, distance=80,
                        patrol=[
                            {"x": 180, "y": 75, "angle": 180},
                            {"x": 120, "y": 75, "angle": 180},
                            {"x": 120, "y": 75, "angle": 0},
                            {"x": 180, "y": 75, "angle": 0},
                        ]),
            # Guardia 2: Patrulla vertical en el corredor
            _make_guard(230, 65, 10, 10, angle=90, fov=60, distance=70,
                        patrol=[
                            {"x": 230, "y": 65, "angle": 90},
                            {"x": 230, "y": 140, "angle": 90},
                            {"x": 230, "y": 65, "angle": 270},
                        ]),
            # Guardia 3: Patrulla horizontal alta en la sala central
            _make_guard(400, 35, 10, 10, angle=180, fov=80, distance=90,
                        patrol=[
                            {"x": 400, "y": 35, "angle": 180},
                            {"x": 310, "y": 35, "angle": 180},
                            {"x": 310, "y": 35, "angle": 0},
                            {"x": 400, "y": 35, "angle": 0},
                        ]),
            # Guardia 4: Patrulla horizontal media en la sala central
            _make_guard(310, 110, 10, 10, angle=0, fov=65, distance=75,
                        patrol=[
                            {"x": 310, "y": 110, "angle": 0},
                            {"x": 400, "y": 110, "angle": 0},
                            {"x": 400, "y": 110, "angle": 180},
                            {"x": 310, "y": 110, "angle": 180},
                        ]),
            # Guardia 5: Patrulla vertical cubriendo el paso previo a la meta
            _make_guard(580, 40, 10, 10, angle=90, fov=75, distance=80,
                        patrol=[
                            {"x": 580, "y": 40, "angle": 90},
                            {"x": 580, "y": 140, "angle": 90},
                            {"x": 580, "y": 40, "angle": 270},
                        ]),
            # Guardia 6: Patrulla en 'L' patrullando el acceso final
            _make_guard(700, 80, 10, 10, angle=180, fov=70, distance=85,
                        patrol=[
                            {"x": 700, "y": 80, "angle": 180},
                            {"x": 630, "y": 80, "angle": 90},
                            {"x": 630, "y": 160, "angle": 0},
                            {"x": 700, "y": 160, "angle": 270},
                            {"x": 700, "y": 80, "angle": 180},
                        ]),
        ]

    def on_input(self, input_id: str, input_data) -> None:
        self.player_entity.on_input(input_id, input_data)

        speed = 60.0
        if input_id == "move_up":
            if input_data.pressed:
                self.player_speed_y = -speed
            elif input_data.released:
                self.player_speed_y = 0.0
        elif input_id == "move_down":
            if input_data.pressed:
                self.player_speed_y = speed
            elif input_data.released:
                self.player_speed_y = 0.0
        elif input_id == "move_right":
            if input_data.pressed:
                self.player_speed_x = speed
            elif input_data.released:
                self.player_speed_x = 0.0
        elif input_id == "move_left":
            if input_data.pressed:
                self.player_speed_x = -speed
            elif input_data.released:
                self.player_speed_x = 0.0

    def update(self, dt: float) -> None:
        if getattr(self, "completed", False):
            return

        # Si el tiempo se agota, reiniciamos al jugador y reseteamos el tiempo
        if self.timer <= 0:
            self._reset_player()
            self.timer = 45.0

        self.player_entity.update(dt)
        self._update_player_movement(dt)
        self._update_guards(dt)
        self._check_detection()

        if self._check_goal():
            return

        self._update_camera(dt)

        if self.detected_timer > 0:
            self.detected_timer -= dt

    def _update_player_movement(self, dt: float) -> None:
        # Movimiento horizontal
        dx = self.player_speed_x * dt
        self.player_entity.x += dx
        for obs in self.obstacles:
            if self.player_entity.collision_rect.colliderect(obs):
                if dx > 0:
                    self.player_entity.x = obs.left - 4 - self.player_entity.collision_rect.width
                elif dx < 0:
                    self.player_entity.x = obs.right - 4

        # Movimiento vertical
        dy = self.player_speed_y * dt
        self.player_entity.y += dy
        for obs in self.obstacles:
            if self.player_entity.collision_rect.colliderect(obs):
                if dy > 0:
                    self.player_entity.y = obs.top - 15 - self.player_entity.collision_rect.height
                elif dy < 0:
                    self.player_entity.y = obs.bottom - 15

    def _update_guards(self, dt: float) -> None:
        for guard in self.guards:
            patrol = guard["patrol"]
            is_moving = False
            if patrol is not None:
                wp = patrol[guard["patrol_index"]]
                tx, ty = float(wp["x"]), float(wp["y"])
                gx, gy = guard["fx"], guard["fy"]

                dist = math.hypot(tx - gx, ty - gy)
                if dist < 1.0:
                    guard["fx"] = tx
                    guard["fy"] = ty
                    guard["angle"] = wp["angle"]
                    guard["patrol_index"] = (guard["patrol_index"] + 1) % len(patrol)
                else:
                    is_moving = True
                    speed = guard["patrol_speed"] * dt
                    ratio = min(speed / dist, 1.0)
                    guard["fx"] += (tx - gx) * ratio
                    guard["fy"] += (ty - gy) * ratio
                    guard["angle"] = math.degrees(math.atan2(ty - gy, tx - gx))

            guard["rect"].x = int(guard["fx"])
            guard["rect"].y = int(guard["fy"])

            actor = guard["actor"]
            actor.x = guard["fx"]
            actor.y = guard["fy"]

            ang = guard["angle"] % 360
            if 45 <= ang < 135:
                actor.direction = "down"
            elif 135 <= ang < 225:
                actor.direction = "left"
            elif 225 <= ang < 315:
                actor.direction = "up"
            else:
                actor.direction = "right"

            if hasattr(actor, "update"):
                actor.update(dt, is_moving=is_moving)

    def _check_detection(self) -> None:
        px, py = self.player_entity.collision_rect.center

        for guard in self.guards:
            gx, gy = guard["rect"].center

            dist = math.hypot(px - gx, py - gy)
            if dist > guard["distance"] or dist == 0:
                continue

            vx, vy = px - gx, py - gy
            rad = math.radians(guard["angle"])
            fx, fy = math.cos(rad), math.sin(rad)

            dot = vx * fx + vy * fy
            cos_to_player = max(-1.0, min(1.0, dot / dist))
            angle_diff = math.degrees(math.acos(cos_to_player))

            if angle_diff > guard["fov"] / 2.0:
                continue

            if line_of_sight_blocked((gx, gy), (px, py), self.obstacles):
                continue

            self._reset_player()
            break

    def _check_goal(self) -> bool:
        if getattr(self, "completed", False):
            return True
        if self.player_entity.collision_rect.colliderect(self.goal):
            self.completed = True
            Timer.clear()
            pygame.mixer.music.stop()  # Stop music on completion
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
            pygame.mixer_music.stop()
            self.state_machine.pop()
            return True
        return False

    def _reset_player(self) -> None:
        self.player_entity.x = float(self.player_spawn[0])
        self.player_entity.y = float(self.player_spawn[1])
        self.player_speed_x = 0.0
        self.player_speed_y = 0.0
        self.detected_timer = 0.6

    def _update_camera(self, dt: float) -> None:
        self.camera.x = self.player_entity.x
        self.camera.y = self.player_entity.y
        self.camera.update(dt)

    def _draw_tiled_floor(self, surface: pygame.Surface) -> None:
        """Dibuja un patrón de suelo de madera coherente con el mapa del nightclub."""
        cam = self.camera
        tile_size = 16
        
        floor_color_1 = (175, 90, 40)
        floor_color_2 = (165, 80, 35)

        start_x = max(0, int(cam.x - self.vw / 2) // tile_size * tile_size)
        end_x = min(self.world_width, int(cam.x + self.vw / 2) + tile_size)
        start_y = max(0, int(cam.y - self.vh / 2) // tile_size * tile_size)
        end_y = min(self.world_height, int(cam.y + self.vh / 2) + tile_size)

        for x in range(start_x, end_x, tile_size):
            for y in range(start_y, end_y, tile_size):
                rect = pygame.Rect(x, y, tile_size, tile_size)
                screen_rect = cam.apply(rect)
                color = floor_color_1 if ((x // tile_size) + (y // tile_size)) % 2 == 0 else floor_color_2
                pygame.draw.rect(surface, color, screen_rect)

    def render(self, surface: pygame.Surface) -> None:
        # 1. Fondo base y suelo con textura de baldosas
        surface.fill((20, 15, 25))
        self._draw_tiled_floor(surface)

        cam = self.camera

        # 2. Zona Objetivo (Oficina de Blackwood)
        goal_screen = cam.apply(self.goal)
        pygame.draw.rect(surface, (140, 40, 40), goal_screen)
        pygame.draw.rect(surface, (230, 190, 90), goal_screen, 1)

        # 3. Obstáculos / Coberturas
        for obs in self.obstacles:
            screen_rect = cam.apply(obs)
            pygame.draw.rect(surface, (110, 55, 25), screen_rect)
            if screen_rect.width > 12 and screen_rect.height > 12:
                inner_rect = screen_rect.inflate(-4, -4)
                pygame.draw.rect(surface, (35, 120, 85), inner_rect)
            pygame.draw.rect(surface, (60, 30, 10), screen_rect, 1)

        # 4. Conos de visión (por debajo de los personajes)
        for guard in self.guards:
            self._render_fov(surface, guard, cam)

        # 5. Dibujar Guardias (usando Actor)
        for guard in self.guards:
            guard["actor"].render(surface, camera=cam)

        # 6. Dibujar a Gallagher (usando Player)
        self.player_entity.render(surface, camera=cam)

        # 7. Capa de Oscuridad / Vignette Noir
        darkness = pygame.Surface((self.vw, self.vh), pygame.SRCALPHA)
        darkness.fill((10, 10, 20, 110))
        surface.blit(darkness, (0, 0))

        # 8. Flash de Detección
        if self.detected_timer > 0:
            alpha = int(140 * (self.detected_timer / 0.6))
            flash = pygame.Surface((self.vw, self.vh), pygame.SRCALPHA)
            flash.fill((220, 40, 40, alpha))
            surface.blit(flash, (0, 0))

        # 9. Renderizado del Temporizador
        timer_color = (196, 72, 57) if self.timer <= 10 else (218, 214, 198)
        render_text(
            surface, 
            f"TIME: {int(self.timer)}", 
            settings.FONTS["medium"], 
            self.vw - 70, 
            10, 
            timer_color
        )

    def _render_fov(
        self, surface: pygame.Surface, guard: Dict, cam: Camera
    ) -> None:
        """Renderiza los conos de visión como luz de linterna ámbar cálida."""
        gx, gy = guard["rect"].center
        rad = math.radians(guard["angle"])
        half_fov = math.radians(guard["fov"] / 2.0)
        dist = guard["distance"]

        num_segments = 12
        world_points = [(gx, gy)]

        for i in range(num_segments + 1):
            frac = i / num_segments
            a = rad - half_fov + frac * (2 * half_fov)
            wx = gx + math.cos(a) * dist
            wy = gy + math.sin(a) * dist
            world_points.append((wx, wy))

        screen_points = [cam.world_to_screen(p) for p in world_points]
        int_points = [(int(p[0]), int(p[1])) for p in screen_points]

        if len(int_points) >= 3:
            xs = [p[0] for p in int_points]
            ys = [p[1] for p in int_points]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            w = max_x - min_x + 1
            h = max_y - min_y + 1

            if w > 0 and h > 0:
                fov_surf = pygame.Surface((w, h), pygame.SRCALPHA)
                shifted = [(p[0] - min_x, p[1] - min_y) for p in int_points]
                pygame.draw.polygon(fov_surf, (230, 180, 70, 45), shifted)
                pygame.draw.polygon(fov_surf, (255, 210, 100, 90), shifted, 1)
                surface.blit(fov_surf, (min_x, min_y))