import math
import random
from typing import Any, Callable, Dict, List, Optional

import pygame

from gale.animation import Animation
from gale.input_handler import KeyboardData
from gale.state import BaseState, StateMachine

import settings
from src.entity.Actor import Actor


class CombatEntity(Actor):
    def __init__(self, x: float, y: float, texture: str, name: str) -> None:
        super().__init__(x, y, texture, name)
        self.animations: Dict[str, Animation] = {}
        self.current_animation: Optional[Animation] = None
        self.state_machine: Optional[StateMachine] = None
        self.facing = "right"
        self.hp: int = 3
        self.max_hp: int = 3
        self.invulnerable_timer: float = 0.0

    def change_state(self, name: str) -> None:
        if self.state_machine:
            self.state_machine.change(name)

    def change_animation(self, name: str) -> None:
        if name in self.animations:
            self.current_animation = self.animations[name]
            self.current_animation.reset()

    def update(self, dt: float) -> None:
        if self.invulnerable_timer > 0:
            self.invulnerable_timer = max(0.0, self.invulnerable_timer - dt)
        if self.state_machine:
            self.state_machine.update(dt)
        if self.current_animation:
            self.current_animation.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        if not self.current_animation:
            return

        # Parpadeo por invulnerabilidad tras ser alcanzado
        if self.invulnerable_timer > 0 and (pygame.time.get_ticks() % 160 < 80):
            return

        texture = settings.TEXTURES[self.texture]
        frame = settings.FRAMES[self.texture][self.current_animation.get_current_frame()]

        image = pygame.Surface((frame.width, frame.height), pygame.SRCALPHA)
        image.blit(texture, (0, 0), frame)

        # Spritesheets diseñados mirando a la derecha por defecto que requieren volteo al mirar a la izquierda
        RIGHT_FACING_TEXTURES = (
            "gallagher_shoot",
            "bandit_hit",
            "steiger",
            "steiger_shot",
            "steiger_dash",
        )
        if self.texture in RIGHT_FACING_TEXTURES and self.facing == "left":
            image = pygame.transform.flip(image, True, False)

        surface.blit(image, (self.x, self.y))


# ── Estados de Gallagher ───────────────────────────────────────────────────

class GallagherCombatState(BaseState):
    def __init__(self, entity: CombatEntity, sm: StateMachine):
        self.entity = entity
        self.sm = sm


class GallagherIdle(GallagherCombatState):
    def enter(self) -> None:
        if self.entity.texture != "gallagher":
            self.entity.texture = "gallagher"
        if not self.entity.current_animation:
            self.entity.change_animation(f"idle-{self.entity.facing}")

    def update(self, dt: float) -> None:
        pass


class GallagherShoot(GallagherCombatState):
    def enter(self) -> None:
        self.entity.texture = "gallagher_shoot"
        self.entity.change_animation("shoot")
        self.shot_fired = False

    def update(self, dt: float) -> None:
        if self.entity.current_animation.current_frame_index >= 2 and not self.shot_fired:
            self.shot_fired = True
            if hasattr(self.entity, "on_shoot"):
                self.entity.on_shoot()

        if self.entity.current_animation.times_played >= self.entity.current_animation.loops:
            self.sm.change("idle")


# ── Arquitectura de Comportamiento de Enemigo (Strategy) ────────────────────

class EnemyBehavior:
    def __init__(
        self,
        entity: CombatEntity,
        world_state: BaseState,
        combat_state: "CombatState",
    ) -> None:
        self.entity = entity
        self.world_state = world_state
        self.combat_state = combat_state

    def setup(self) -> None:
        raise NotImplementedError

    def update(self, dt: float) -> None:
        pass

    def on_hit_by_bullet(self) -> None:
        raise NotImplementedError

    def get_display_name(self) -> str:
        return self.entity.name

    def get_collision_rect(self) -> pygame.Rect:
        return pygame.Rect(self.entity.x, self.entity.y, 24, 30)


# ── Comportamiento del Matón del Callejón (Bandit) ──────────────────────────

class BanditChase(BaseState):
    def __init__(
        self,
        entity: CombatEntity,
        sm: StateMachine,
        world_state: BaseState,
        combat_state: "CombatState",
    ) -> None:
        self.entity = entity
        self.sm = sm
        self.world_state = world_state
        self.combat_state = combat_state

    def enter(self) -> None:
        self.entity.texture = "bandit"
        self.entity.facing = None

    def update(self, dt: float) -> None:
        target = self.combat_state.gallagher
        speed = 42.0

        dx = target.x - self.entity.x
        dy = target.y - self.entity.y
        dist = math.hypot(dx, dy)

        if dist > 0:
            target_x = self.entity.x + (dx / dist) * speed * dt
            target_y = self.entity.y + (dy / dist) * speed * dt

            test_rect = pygame.Rect(0, 0, 13, 13)

            # Eje X
            test_rect.x = round(target_x + 9)
            test_rect.y = round(self.entity.y + 24)
            if self.world_state.region.is_walkable(test_rect):
                self.entity.x = target_x

            # Eje Y
            test_rect.x = round(self.entity.x + 9)
            test_rect.y = round(target_y + 24)
            if self.world_state.region.is_walkable(test_rect):
                self.entity.y = target_y

        facing = "right" if dx > 0 else "left"
        if facing != self.entity.facing or not self.entity.current_animation:
            self.entity.facing = facing
            self.entity.change_animation(f"walk_{facing}")

        if dist < 20:
            self.sm.change("attack")


class BanditAttack(BaseState):
    def __init__(
        self,
        entity: CombatEntity,
        sm: StateMachine,
        world_state: BaseState,
        combat_state: "CombatState",
    ) -> None:
        self.entity = entity
        self.sm = sm
        self.world_state = world_state
        self.combat_state = combat_state

    def enter(self) -> None:
        self.entity.texture = "bandit_hit"
        self.entity.change_animation("attack")
        self.has_hit = False

    def update(self, dt: float) -> None:
        if self.entity.current_animation.current_frame_index >= 2 and not self.has_hit:
            self.has_hit = True
            self.combat_state.damage_player(1)

        if self.entity.current_animation.times_played >= self.entity.current_animation.loops:
            self.sm.change("chase")


class BanditHit(BaseState):
    def __init__(
        self,
        entity: CombatEntity,
        sm: StateMachine,
        world_state: BaseState,
        combat_state: "CombatState",
    ) -> None:
        self.entity = entity
        self.sm = sm
        self.world_state = world_state
        self.combat_state = combat_state

    def enter(self) -> None:
        self.entity.texture = "bandit"
        self.entity.change_animation("idle")
        self.entity.hp -= 1
        self.timer = 0.45
        if self.entity.hp <= 0:
            self.combat_state.on_enemy_defeated()

    def update(self, dt: float) -> None:
        if self.entity.hp <= 0:
            return

        self.timer -= dt
        if self.timer <= 0:
            self.sm.change("chase")


class BanditBehavior(EnemyBehavior):
    def setup(self) -> None:
        self.entity.texture = "bandit"
        self.entity.hp = 3
        self.entity.max_hp = 3
        self.entity.animations = {
            "idle": Animation([0], 1.0, loops=None),
            "walk_right": Animation([6, 7, 8, 9, 10, 11], 0.15, loops=None),
            "walk_left": Animation([12, 13, 14, 15, 16, 17], 0.15, loops=None),
            "attack": Animation([0, 1, 2, 3], 0.1, loops=1),
        }
        self.entity.state_machine = StateMachine({
            "chase": lambda sm: BanditChase(self.entity, sm, self.world_state, self.combat_state),
            "attack": lambda sm: BanditAttack(self.entity, sm, self.world_state, self.combat_state),
            "hit": lambda sm: BanditHit(self.entity, sm, self.world_state, self.combat_state),
        })
        self.entity.change_state("chase")

    def on_hit_by_bullet(self) -> None:
        if self.entity.state_machine and not isinstance(self.entity.state_machine.current, BanditHit):
            self.entity.change_state("hit")

    def get_display_name(self) -> str:
        return "MATÓN DE BLACKWOOD"

    def get_collision_rect(self) -> pygame.Rect:
        return pygame.Rect(self.entity.x + 3, self.entity.y + 2, 25, 35)


# ── Comportamiento del Jefe Final: Niko Stieger ─────────────────────────────

class SteigerChase(BaseState):
    def __init__(
        self,
        entity: CombatEntity,
        sm: StateMachine,
        world_state: BaseState,
        combat_state: "CombatState",
    ) -> None:
        self.entity = entity
        self.sm = sm
        self.world_state = world_state
        self.combat_state = combat_state
        self.shoot_cooldown = random.uniform(2.0, 3.2)
        self.dash_cooldown = random.uniform(3.0, 4.5)

    def enter(self) -> None:
        self.entity.texture = "steiger"
        self.entity.change_animation("walk")

    def update(self, dt: float) -> None:
        target = self.combat_state.gallagher
        speed = 46.0

        dx = target.x - self.entity.x
        dy = target.y - self.entity.y
        dist = math.hypot(dx, dy)

        self.entity.facing = "right" if dx >= 0 else "left"

        if dist > 0:
            target_x = self.entity.x + (dx / dist) * speed * dt
            target_y = self.entity.y + (dy / dist) * speed * dt

            test_rect = pygame.Rect(0, 0, 14, 14)

            # Eje X
            test_rect.x = round(target_x + 3)
            test_rect.y = round(self.entity.y + 14)
            if self.world_state.region.is_walkable(test_rect):
                self.entity.x = target_x

            # Eje Y
            test_rect.x = round(self.entity.x + 3)
            test_rect.y = round(target_y + 14)
            if self.world_state.region.is_walkable(test_rect):
                self.entity.y = target_y

        self.shoot_cooldown -= dt
        self.dash_cooldown -= dt

        # Decisión táctica: Dash cuando está a media distancia
        if self.dash_cooldown <= 0 and 35 <= dist <= 110:
            self.sm.change("dash")
            return

        # Decisión táctica: Ráfaga Thompson
        if self.shoot_cooldown <= 0 and dist > 40:
            self.sm.change("shoot")
            return

        # Golpe si está a rango melee
        if dist < 20:
            self.combat_state.damage_player(1)


class SteigerShoot(BaseState):
    """Ataque con ametralladora Thompson: ráfaga de proyectiles hacia Gallagher."""

    def __init__(
        self,
        entity: CombatEntity,
        sm: StateMachine,
        world_state: BaseState,
        combat_state: "CombatState",
    ) -> None:
        self.entity = entity
        self.sm = sm
        self.world_state = world_state
        self.combat_state = combat_state

    def enter(self) -> None:
        self.entity.texture = "steiger_shot"
        self.entity.change_animation("shoot")

        target = self.combat_state.gallagher
        dx = target.x - self.entity.x
        self.entity.facing = "right" if dx >= 0 else "left"

        self.shots_to_fire = 3
        self.shots_fired = 0
        self.burst_timer = 0.08
        self.post_burst_timer = 0.45

    def update(self, dt: float) -> None:
        if self.shots_fired < self.shots_to_fire:
            self.burst_timer -= dt
            if self.burst_timer <= 0:
                self.burst_timer = 0.14
                self.shots_fired += 1

                # Disparar bala enemiga hacia la posición actual de Gallagher
                target = self.combat_state.gallagher
                gun_x = self.entity.x + (18 if self.entity.facing == "right" else 2)
                gun_y = self.entity.y + 11

                tdx = target.x + 8 - gun_x
                tdy = target.y + 14 - gun_y
                tdist = max(1.0, math.hypot(tdx, tdy))

                speed = 220.0
                vx = (tdx / tdist) * speed
                vy = (tdy / tdist) * speed

                self.combat_state.enemy_bullets.append({
                    "x": gun_x,
                    "y": gun_y,
                    "vx": vx,
                    "vy": vy,
                })
        else:
            self.post_burst_timer -= dt
            if self.post_burst_timer <= 0:
                self.sm.change("chase")


class SteigerDash(BaseState):
    """Embestida veloz hacia Gallagher que causa daño por impacto."""

    def __init__(
        self,
        entity: CombatEntity,
        sm: StateMachine,
        world_state: BaseState,
        combat_state: "CombatState",
    ) -> None:
        self.entity = entity
        self.sm = sm
        self.world_state = world_state
        self.combat_state = combat_state

    def enter(self) -> None:
        self.entity.texture = "steiger_dash"
        self.entity.change_animation("dash")

        target = self.combat_state.gallagher
        dx = target.x - self.entity.x
        dy = target.y - self.entity.y
        dist = max(1.0, math.hypot(dx, dy))

        self.entity.facing = "right" if dx >= 0 else "left"
        dash_speed = 155.0
        self.dash_vx = (dx / dist) * dash_speed
        self.dash_vy = (dy / dist) * dash_speed

        self.duration = 0.42
        self.has_dealt_damage = False

    def update(self, dt: float) -> None:
        self.duration -= dt

        # Movimiento con colisiones del entorno
        target_x = self.entity.x + self.dash_vx * dt
        target_y = self.entity.y + self.dash_vy * dt

        test_rect = pygame.Rect(0, 0, 14, 14)
        test_rect.x = round(target_x + 3)
        test_rect.y = round(self.entity.y + 14)
        if self.world_state.region.is_walkable(test_rect):
            self.entity.x = target_x

        test_rect.x = round(self.entity.x + 3)
        test_rect.y = round(target_y + 14)
        if self.world_state.region.is_walkable(test_rect):
            self.entity.y = target_y

        # Colisión con Gallagher
        target = self.combat_state.gallagher
        dist = math.hypot(target.x - self.entity.x, target.y - self.entity.y)
        if dist < 22 and not self.has_dealt_damage:
            self.has_dealt_damage = True
            self.combat_state.damage_player(1)

        if self.duration <= 0:
            self.sm.change("chase")


class SteigerHit(BaseState):
    """Reacción al ser alcanzado por un proyectil de Gallagher."""

    def __init__(
        self,
        entity: CombatEntity,
        sm: StateMachine,
        world_state: BaseState,
        combat_state: "CombatState",
    ) -> None:
        self.entity = entity
        self.sm = sm
        self.world_state = world_state
        self.combat_state = combat_state

    def enter(self) -> None:
        self.entity.texture = "steiger"
        self.entity.change_animation("idle")
        self.entity.hp -= 1
        self.timer = 0.4
        if self.entity.hp <= 0:
            self.combat_state.on_enemy_defeated()

    def update(self, dt: float) -> None:
        if self.entity.hp <= 0:
            return

        self.timer -= dt
        if self.timer <= 0:
            self.sm.change("chase")


class SteigerBehavior(EnemyBehavior):
    def setup(self) -> None:
        self.entity.texture = "steiger"
        self.entity.hp = 5
        self.entity.max_hp = 5
        self.entity.animations = {
            "idle": Animation([0, 1, 2, 3, 4], 0.18, loops=None),
            "walk": Animation([6, 7, 8, 9, 10, 11], 0.14, loops=None),
            "shoot": Animation([0, 1, 2, 3, 4], 0.12, loops=1),
            "dash": Animation([0, 1, 2, 3], 0.1, loops=None),
        }
        self.entity.state_machine = StateMachine({
            "chase": lambda sm: SteigerChase(self.entity, sm, self.world_state, self.combat_state),
            "shoot": lambda sm: SteigerShoot(self.entity, sm, self.world_state, self.combat_state),
            "dash": lambda sm: SteigerDash(self.entity, sm, self.world_state, self.combat_state),
            "hit": lambda sm: SteigerHit(self.entity, sm, self.world_state, self.combat_state),
        })
        self.entity.change_state("chase")

    def on_hit_by_bullet(self) -> None:
        if self.entity.state_machine and not isinstance(self.entity.state_machine.current, SteigerHit):
            self.entity.change_state("hit")

    def get_display_name(self) -> str:
        return "NIKO STEIGER 'EL TIGRE'"

    def get_collision_rect(self) -> pygame.Rect:
        return pygame.Rect(self.entity.x + 2, self.entity.y + 2, 18, 26)


# ── Contenedor Principal de Combate (CombatState) ───────────────────────────

class CombatState(BaseState):
    def enter(
        self,
        params: Optional[Dict[str, Any]] = None,
        world_state: Optional[BaseState] = None,
        on_complete: Optional[Callable[[], None]] = None,
        **kwargs: Any,
    ) -> None:

        music_path = settings.BASE_DIR / "assets" / "sounds" / "persecution.mp3"
        if music_path.exists():
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(loops=-1)

        if params is None:
            params = {}

        self.world_state: BaseState = params.get("world_state", world_state or kwargs.get("world_state"))
        self.on_victory: Optional[Callable[[], None]] = params.get(
            "on_victory_callback", on_complete or kwargs.get("on_complete")
        )
        self.enemy_id: str = params.get("enemy_id", kwargs.get("enemy_id", "bandit"))
        self.arena_layout: str = params.get("arena_layout", kwargs.get("arena_layout", "alley"))
        self.player_max_health: int = params.get("player_health", kwargs.get("player_health", 3))

        # Configuración de Gallagher en su posición actual del mundo
        self.spawn_px = getattr(self.world_state.player, "x", 60)
        self.spawn_py = getattr(self.world_state.player, "y", 100)

        self.gallagher = CombatEntity(self.spawn_px, self.spawn_py, "gallagher", "Gallagher")
        self.gallagher.hp = self.player_max_health
        self.gallagher.max_hp = self.player_max_health
        self.gallagher.animations = {
            "idle-right": Animation([6], 1.0, loops=None),
            "idle-left": Animation([9], 1.0, loops=None),
            "idle-up": Animation([3], 1.0, loops=None),
            "idle-down": Animation([0], 1.0, loops=None),
            "walk-down": Animation([0, 1, 0, 2], 0.15, loops=None),
            "walk-up": Animation([3, 4, 3, 5], 0.15, loops=None),
            "walk-right": Animation([6, 7, 6, 8], 0.15, loops=None),
            "walk-left": Animation([9, 10, 9, 11], 0.15, loops=None),
            "shoot": Animation([0, 1, 2, 3], 0.15, loops=1),
        }
        self.gallagher.state_machine = StateMachine({
            "idle": lambda sm: GallagherIdle(self.gallagher, sm),
            "shoot": lambda sm: GallagherShoot(self.gallagher, sm),
        })
        self.gallagher.on_shoot = self._on_gallagher_shoot
        self.gallagher.change_state("idle")

        # Configuración del Enemigo según estrategia seleccionada
        self._setup_enemy_spawn()

        self.bullets: List[Dict[str, float]] = []
        self.enemy_bullets: List[Dict[str, float]] = []
        self.status_text: str = ""
        self.held_keys: Dict[str, bool] = {
            "move_up": False,
            "move_down": False,
            "move_left": False,
            "move_right": False,
        }

    def _setup_enemy_spawn(self) -> None:
        # Buscar posición transitable segura cerca de Gallagher
        self.spawn_ex = self.spawn_px + 70
        self.spawn_ey = self.spawn_py

        test_rect = pygame.Rect(round(self.spawn_ex + 4), round(self.spawn_ey + 14), 14, 14)
        if hasattr(self.world_state, "region") and not self.world_state.region.is_walkable(test_rect):
            self.spawn_ex = self.spawn_px - 70
            test_rect.x = round(self.spawn_ex + 4)
            if not self.world_state.region.is_walkable(test_rect):
                self.spawn_ex, self.spawn_ey = self.spawn_px, self.spawn_py + 60

        enemy_texture = "steiger" if self.enemy_id == "steiger" else "bandit"
        enemy_name = "Niko Stieger" if self.enemy_id == "steiger" else "Bandit"
        self.enemy = CombatEntity(self.spawn_ex, self.spawn_ey, enemy_texture, enemy_name)

        if self.enemy_id == "steiger":
            self.enemy_behavior: EnemyBehavior = SteigerBehavior(self.enemy, self.world_state, self)
        else:
            self.enemy_behavior = BanditBehavior(self.enemy, self.world_state, self)

        self.enemy_behavior.setup()

    def damage_player(self, amount: int = 1) -> None:
        if self.gallagher.invulnerable_timer > 0 or self.status_text:
            return

        self.gallagher.hp -= amount
        self.gallagher.invulnerable_timer = 1.2

        if self.gallagher.hp <= 0:
            self.gallagher.hp = 0
            self.status_text = "¡Has sido derrotado! Presiona ESPACIO para reintentar."

    def on_enemy_defeated(self) -> None:
        if self.enemy_id == "steiger":
            self.status_text = "¡Has derrotado a Niko Stieger! Presiona ESPACIO para continuar."
        else:
            self.status_text = "¡Has derrotado al bandido! Presiona ESPACIO para continuar."

    def _on_gallagher_shoot(self) -> None:
        vx = 300.0 if self.gallagher.facing != "left" else -300.0
        offset_x = 20 if vx > 0 else -4
        self.bullets.append({
            "x": self.gallagher.x + offset_x,
            "y": self.gallagher.y + 15,
            "vx": vx,
            "vy": 0.0,
        })

    def update(self, dt: float) -> None:
        if self.status_text:
            return

        self.gallagher.update(dt)
        self.enemy.update(dt)
        self.enemy_behavior.update(dt)

        # Movimiento de Gallagher
        if not (self.gallagher.state_machine and isinstance(self.gallagher.state_machine.current, GallagherShoot)):
            speed = 82.0
            dx = float(self.held_keys["move_right"] - self.held_keys["move_left"])
            dy = float(self.held_keys["move_down"] - self.held_keys["move_up"])

            if dx and dy:
                dx *= 0.7071
                dy *= 0.7071

            target_x = self.gallagher.x + dx * speed * dt
            target_y = self.gallagher.y + dy * speed * dt

            test_rect = pygame.Rect(0, 0, 13, 13)

            # Eje X
            test_rect.x = round(target_x + 3)
            test_rect.y = round(self.gallagher.y + 15)
            if hasattr(self.world_state, "region") and self.world_state.region.is_walkable(test_rect):
                self.gallagher.x = target_x

            # Eje Y
            test_rect.x = round(self.gallagher.x + 3)
            test_rect.y = round(target_y + 15)
            if hasattr(self.world_state, "region") and self.world_state.region.is_walkable(test_rect):
                self.gallagher.y = target_y

            # Animaciones de Gallagher
            if dx < 0:
                self.gallagher.facing = "left"
                anim = "walk-left"
            elif dx > 0:
                self.gallagher.facing = "right"
                anim = "walk-right"
            elif dy < 0:
                self.gallagher.facing = "up"
                anim = "walk-up"
            elif dy > 0:
                self.gallagher.facing = "down"
                anim = "walk-down"
            else:
                anim = f"idle-{self.gallagher.facing}"

            if not self.gallagher.current_animation or self.gallagher.animations.get(anim) != self.gallagher.current_animation:
                self.gallagher.change_animation(anim)

        # Actualizar balas del jugador
        enemy_rect = self.enemy_behavior.get_collision_rect()
        for b in self.bullets[:]:
            b["x"] += b["vx"] * dt
            b["y"] += b["vy"] * dt

            brect = pygame.Rect(b["x"], b["y"], 5, 2)
            if brect.colliderect(enemy_rect):
                if b in self.bullets:
                    self.bullets.remove(b)
                self.enemy_behavior.on_hit_by_bullet()
            elif b["x"] > settings.VIRTUAL_WIDTH or b["x"] < 0:
                if b in self.bullets:
                    self.bullets.remove(b)

        # Actualizar balas enemigas (Thompson de Stieger)
        g_collision_rect = pygame.Rect(self.gallagher.x + 3, self.gallagher.y + 4, 13, 24)
        for eb in self.enemy_bullets[:]:
            eb["x"] += eb["vx"] * dt
            eb["y"] += eb["vy"] * dt

            # Colisión con Gallagher
            eb_rect = pygame.Rect(eb["x"], eb["y"], 4, 3)
            if eb_rect.colliderect(g_collision_rect):
                if eb in self.enemy_bullets:
                    self.enemy_bullets.remove(eb)
                self.damage_player(1)
                continue

            # Colisión con muros/obstáculos del entorno
            wall_rect = pygame.Rect(round(eb["x"]), round(eb["y"]), 2, 2)
            if hasattr(self.world_state, "region") and not self.world_state.region.is_walkable(wall_rect):
                if eb in self.enemy_bullets:
                    self.enemy_bullets.remove(eb)
                continue

            # Fuera de pantalla
            if (
                eb["x"] < -20
                or eb["x"] > settings.VIRTUAL_WIDTH + 20
                or eb["y"] < -20
                or eb["y"] > settings.VIRTUAL_HEIGHT + 20
            ):
                if eb in self.enemy_bullets:
                    self.enemy_bullets.remove(eb)

    def render(self, surface: pygame.Surface) -> None:
        # 1. Fondo de la arena usando el mapa real de tiles del mundo
        if hasattr(self.world_state, "region") and hasattr(self.world_state, "camera"):
            self.world_state.region.tilemap.render(surface, self.world_state.camera)

        # 2. Entidades
        self.gallagher.render(surface)

        # Parpadeo del enemigo si está en estado hit
        if self.enemy.hp > 0:
            is_hit = self.enemy.state_machine and (
                isinstance(self.enemy.state_machine.current, (BanditHit, SteigerHit))
            )
            if not is_hit or (pygame.time.get_ticks() % 160 < 80):
                self.enemy.render(surface)

        # 3. Proyectiles
        # Balas de Gallagher (doradas)
        for b in self.bullets:
            pygame.draw.rect(surface, (255, 220, 60), (b["x"], b["y"], 4, 2))
            pygame.draw.rect(surface, (255, 255, 200), (b["x"] + 1, b["y"], 2, 1))

        # Balas enemigas (rojas/anaranjadas intensas de Thompson)
        for eb in self.enemy_bullets:
            pygame.draw.rect(surface, (240, 60, 20), (eb["x"] - 1, eb["y"] - 1, 5, 4))
            pygame.draw.rect(surface, (255, 230, 80), (eb["x"], eb["y"], 3, 2))

        # 4. HUD de Combate
        self._render_hud(surface)

        # 5. Overlay de Estado (Victoria o Derrota)
        if self.status_text:
            font = settings.FONTS["medium"]
            text = font.render(self.status_text, True, (255, 255, 255))
            rect = text.get_rect(center=(settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT // 2))

            bg = pygame.Rect(rect.x - 12, rect.y - 10, rect.width + 24, rect.height + 20)
            pygame.draw.rect(surface, (15, 15, 18), bg)
            pygame.draw.rect(surface, (200, 160, 90), bg, 2)
            surface.blit(text, rect)

    def _render_hud(self, surface: pygame.Surface) -> None:
        font = settings.FONTS["small"]

        # ── Vida de Gallagher (Arriba a la Izquierda) ──
        salud_text = "GALLAGHER:"
        t_surf = font.render(salud_text, True, (210, 200, 185))
        surface.blit(t_surf, (14, 10))

        # Corazones / Pips de Salud
        pip_x = 14 + t_surf.get_width() + 8
        for i in range(self.gallagher.max_hp):
            color = (215, 55, 45) if i < self.gallagher.hp else (55, 50, 48)
            pygame.draw.rect(surface, color, (pip_x + (i * 12), 11, 9, 9), border_radius=2)
            pygame.draw.rect(surface, (30, 25, 25), (pip_x + (i * 12), 11, 9, 9), 1, border_radius=2)

        # ── Barra de Salud del Enemigo (Arriba a la Derecha) ──
        enemy_name = self.enemy_behavior.get_display_name()
        e_surf = font.render(enemy_name, True, (210, 200, 185))
        ex = settings.VIRTUAL_WIDTH - 14 - e_surf.get_width()
        surface.blit(e_surf, (ex, 10))

        # Pips del Enemigo
        bar_w = self.enemy.max_hp * 12
        bar_x = settings.VIRTUAL_WIDTH - 14 - bar_w
        for i in range(self.enemy.max_hp):
            color = (230, 150, 40) if i < self.enemy.hp else (55, 50, 48)
            pygame.draw.rect(surface, color, (bar_x + (i * 12), 22, 9, 7), border_radius=1)
            pygame.draw.rect(surface, (30, 25, 25), (bar_x + (i * 12), 22, 9, 7), 1, border_radius=1)

    def on_input(self, input_id: str, input_data: Any) -> None:
        if input_id in self.held_keys:
            self.held_keys[input_id] = input_data.pressed or not input_data.released

        if isinstance(input_data, KeyboardData) and not input_data.pressed:
            return

        if self.status_text:
            if input_id in ("space", "enter", "interact", "confirm"):
                if self.enemy.hp <= 0:
                    pygame.mixer.music.stop()
                    self.state_machine.pop()
                    if self.on_victory:
                        self.on_victory()
                else:
                    # Reiniciar encuentro tras derrota
                    self.gallagher.x = self.spawn_px
                    self.gallagher.y = self.spawn_py
                    self.gallagher.hp = self.player_max_health
                    self.gallagher.invulnerable_timer = 0.0
                    self.gallagher.change_state("idle")

                    self.enemy.x = self.spawn_ex
                    self.enemy.y = self.spawn_ey
                    self.enemy.hp = self.enemy.max_hp
                    self.enemy.change_state("chase")

                    self.bullets.clear()
                    self.enemy_bullets.clear()
                    self.status_text = ""
            return

        if input_id == "shoot":
            if self.gallagher.state_machine and not isinstance(
                self.gallagher.state_machine.current, GallagherShoot
            ):
                self.gallagher.change_state("shoot")
