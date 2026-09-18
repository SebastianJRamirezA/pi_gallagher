from typing import Any, Callable, Dict, Optional

import pygame

from gale.animation import Animation
from gale.input_handler import InputData, KeyboardData
from gale.state import BaseState, StateMachine
from gale.timer import Timer

import settings
from src.entity.Actor import Actor


class CombatEntity(Actor):
    def __init__(self, x: float, y: float, texture: str, name: str) -> None:
        super().__init__(x, y, texture, name)
        self.animations: Dict[str, Animation] = {}
        self.current_animation: Optional[Animation] = None
        self.state_machine: Optional[StateMachine] = None
        self.facing = "right"

    def change_state(self, name: str) -> None:
        if self.state_machine:
            self.state_machine.change(name)

    def change_animation(self, name: str) -> None:
        if name in self.animations:
            self.current_animation = self.animations[name]
            self.current_animation.reset()

    def update(self, dt: float) -> None:
        if self.state_machine:
            self.state_machine.update(dt)
        if self.current_animation:
            self.current_animation.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        if not self.current_animation:
            return
            
        texture = settings.TEXTURES[self.texture]
        frame = settings.FRAMES[self.texture][self.current_animation.get_current_frame()]
        
        image = pygame.Surface((frame.width, frame.height), pygame.SRCALPHA)
        image.blit(texture, (0, 0), frame)
        
        # gallagher_shoot and bandit_hit are right-facing spritesheets that need manual flipping
        if self.texture in ("gallagher_shoot", "bandit_hit") and self.facing == "left":
            image = pygame.transform.flip(image, True, False)
            
        surface.blit(image, (self.x, self.y))


class GallagherCombatState(BaseState):
    def __init__(self, entity: CombatEntity, sm: StateMachine):
        self.entity = entity
        self.sm = sm

class GallagherIdle(GallagherCombatState):
    def enter(self) -> None:
        if self.entity.texture != "gallagher":
            self.entity.texture = "gallagher"
        # Animation is managed by CombatState.update
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


class BanditCombatState(BaseState):
    def __init__(self, entity: CombatEntity, sm: StateMachine, world_state: BaseState):
        self.entity = entity
        self.sm = sm
        self.world_state = world_state

class BanditChase(BanditCombatState):
    def enter(self) -> None:
        self.entity.texture = "bandit"
        self.entity.facing = None # Force update to pick the correct walk animation

    def update(self, dt: float) -> None:
        target = self.entity.target
        speed = 40.0
        
        dx = target.x - self.entity.x
        dy = target.y - self.entity.y
        dist = (dx**2 + dy**2)**0.5
        
        if dist > 0:
            target_x = self.entity.x + (dx/dist) * speed * dt
            target_y = self.entity.y + (dy/dist) * speed * dt
            
            # Approximate collision rect for Bandit (14x14 at bottom, like player)
            test_rect = pygame.Rect(0, 0, 13, 13)
            
            # Check X
            test_rect.x = round(target_x + 9) # 31 width -> approx center is 9
            test_rect.y = round(self.entity.y + 24) # 37 height -> approx bottom
            if self.world_state.region.is_walkable(test_rect):
                self.entity.x = target_x
                
            # Check Y
            test_rect.x = round(self.entity.x + 9)
            test_rect.y = round(target_y + 24)
            if self.world_state.region.is_walkable(test_rect):
                self.entity.y = target_y
            
        facing = "right" if dx > 0 else "left"
        if facing != self.entity.facing or not self.entity.current_animation:
            self.entity.facing = facing
            self.entity.change_animation(f"walk_{facing}")
            
        # Hit target
        if dist < 20:
            self.sm.change("attack")

class BanditAttack(BanditCombatState):
    def enter(self) -> None:
        self.entity.texture = "bandit_hit"
        self.entity.change_animation("attack")
        self.has_hit = False

    def update(self, dt: float) -> None:
        if self.entity.current_animation.current_frame_index >= 2 and not self.has_hit:
            self.has_hit = True
            if hasattr(self.entity, "on_hit_player"):
                self.entity.on_hit_player()
                
        if self.entity.current_animation.times_played >= self.entity.current_animation.loops:
            self.sm.change("chase")

class BanditHit(BanditCombatState):
    def enter(self) -> None:
        # Taking damage uses the normal bandit texture but blinks
        self.entity.texture = "bandit"
        self.entity.change_animation("idle")
        self.entity.hp -= 1
        
        # Blink effect timer
        self.timer = 0.5
        
    def update(self, dt: float) -> None:
        if self.entity.hp <= 0:
            if hasattr(self.entity, "on_die"):
                self.entity.on_die()
            return
            
        self.timer -= dt
        if self.timer <= 0:
            self.sm.change("chase")


class CombatState(BaseState):
    def enter(self, world_state: BaseState, on_complete: Callable[[], None]) -> None:
        self.world_state = world_state
        self.on_complete = on_complete
        
        # Setup Gallagher at player's actual position
        self.spawn_px, self.spawn_py = self.world_state.player.x, self.world_state.player.y
        self.gallagher = CombatEntity(self.spawn_px, self.spawn_py, "gallagher", "Gallagher")
        self.gallagher.animations = {
            "idle-right": Animation([6], 1.0, loops=None),
            "idle-left": Animation([9], 1.0, loops=None),
            "idle-up": Animation([3], 1.0, loops=None),
            "idle-down": Animation([0], 1.0, loops=None),
            "walk-down": Animation([0, 1, 0, 2], 0.15, loops=None),
            "walk-up": Animation([3, 4, 3, 5], 0.15, loops=None),
            "walk-right": Animation([6, 7, 6, 8], 0.15, loops=None),
            "walk-left": Animation([9, 10, 9, 11], 0.15, loops=None),
            "shoot": Animation([0, 1, 2, 3], 0.15, loops=1)
        }
        self.gallagher.state_machine = StateMachine({
            "idle": lambda sm: GallagherIdle(self.gallagher, sm),
            "shoot": lambda sm: GallagherShoot(self.gallagher, sm)
        })
        self.gallagher.on_shoot = self._on_gallagher_shoot
        self.gallagher.change_state("idle")
        
        # Setup Bandit nearby
        # Try to find a walkable spot for the bandit around Gallagher
        self.spawn_bx, self.spawn_by = self.spawn_px + 60, self.spawn_py
        test_rect = pygame.Rect(round(self.spawn_bx + 9), round(self.spawn_by + 24), 13, 13)
        if not self.world_state.region.is_walkable(test_rect):
            self.spawn_bx = self.spawn_px - 60
            test_rect.x = round(self.spawn_bx + 9)
            if not self.world_state.region.is_walkable(test_rect):
                self.spawn_bx, self.spawn_by = self.spawn_px, self.spawn_py + 60
                
        self.bandit = CombatEntity(self.spawn_bx, self.spawn_by, "bandit", "Bandit")
        self.bandit.animations = {
            "idle": Animation([0], 1.0, loops=None),
            "walk_right": Animation([6, 7, 8, 9, 10, 11], 0.15, loops=None),
            "walk_left": Animation([12, 13, 14, 15, 16, 17], 0.15, loops=None),
            "attack": Animation([0, 1, 2, 3], 0.1, loops=1)
        }
        self.bandit.state_machine = StateMachine({
            "chase": lambda sm: BanditChase(self.bandit, sm, self.world_state),
            "attack": lambda sm: BanditAttack(self.bandit, sm, self.world_state),
            "hit": lambda sm: BanditHit(self.bandit, sm, self.world_state)
        })
        self.bandit.target = self.gallagher
        self.bandit.hp = 3
        self.bandit.on_hit_player = self._on_player_hit
        self.bandit.on_die = self._on_bandit_die
        self.bandit.change_state("chase")
        
        self.bullets = []
        self.status_text = ""
        self.held_keys = {
            "move_up": False,
            "move_down": False,
            "move_left": False,
            "move_right": False
        }

    def _on_gallagher_shoot(self):
        # Create bullet based on facing direction
        vx = 300 if self.gallagher.facing != "left" else -300
        offset_x = 20 if vx > 0 else -4
        self.bullets.append({
            "x": self.gallagher.x + offset_x,
            "y": self.gallagher.y + 15,
            "vx": vx,
            "vy": 0
        })
        
    def _on_player_hit(self):
        self.status_text = "¡Has sido golpeado! Presiona ESPACIO para reintentar."
        
    def _on_bandit_die(self):
        self.status_text = "¡Has derrotado al bandido! Presiona ESPACIO para continuar."

    def update(self, dt: float) -> None:
        if self.status_text:
            return
            
        self.gallagher.update(dt)
        self.bandit.update(dt)
        
        # Gallagher movement
        if isinstance(self.gallagher.state_machine.current, GallagherShoot):
            # Don't move while shooting
            pass
        else:
            speed = 80.0
            dx = float(self.held_keys["move_right"] - self.held_keys["move_left"])
            dy = float(self.held_keys["move_down"] - self.held_keys["move_up"])
            
            if dx and dy:
                dx *= 0.7071
                dy *= 0.7071
                
            target_x = self.gallagher.x + dx * speed * dt
            target_y = self.gallagher.y + dy * speed * dt
            
            # Collision checks using World's room
            # Approximate collision rect for Gallagher (14x14 at bottom)
            test_rect = pygame.Rect(0, 0, 13, 13)
            
            # Check X
            test_rect.x = round(target_x + 3)
            test_rect.y = round(self.gallagher.y + 15)
            if self.world_state.region.is_walkable(test_rect):
                self.gallagher.x = target_x
                
            # Check Y
            test_rect.x = round(self.gallagher.x + 3)
            test_rect.y = round(target_y + 15)
            if self.world_state.region.is_walkable(test_rect):
                self.gallagher.y = target_y
                
            # Animations
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
                
            # Only change if we're not already playing it
            if not self.gallagher.current_animation or self.gallagher.animations.get(anim) != self.gallagher.current_animation:
                self.gallagher.change_animation(anim)
            
        # Update bullets
        for b in self.bullets[:]:
            b["x"] += b["vx"] * dt
            b["y"] += b["vy"] * dt
            
            # Check collision with bandit
            bx = b["x"]
            by = b["y"]
            bw = 4
            bh = 2
            
            # Simple rect collision
            brect = pygame.Rect(bx, by, bw, bh)
            # Bandit frame size approx 31x37
            bandit_rect = pygame.Rect(self.bandit.x, self.bandit.y, 31, 37)
            
            if brect.colliderect(bandit_rect):
                self.bullets.remove(b)
                if self.bandit.state_machine:
                    self.bandit.change_state("hit")
            elif b["x"] > settings.VIRTUAL_WIDTH or b["x"] < 0:
                self.bullets.remove(b)

    def render(self, surface: pygame.Surface) -> None:
        if self.world_state:
            # Render only the tilemap to hide the real Gallagher and Morales
            self.world_state.region.tilemap.render(surface, self.world_state.camera)
            
        self.gallagher.render(surface)
        
        # Render bandit (with flashing if hit)
        if self.bandit.state_machine and isinstance(self.bandit.state_machine.current, BanditHit):
            if pygame.time.get_ticks() % 200 < 100:
                self.bandit.render(surface)
        else:
            self.bandit.render(surface)
            
        # Render bullets
        for b in self.bullets:
            pygame.draw.rect(surface, (255, 200, 0), (b["x"], b["y"], 4, 2))
            
        # Render status
        if self.status_text:
            font = settings.FONTS["medium"]
            text = font.render(self.status_text, True, (255, 255, 255))
            rect = text.get_rect(center=(settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT // 2))
            
            bg = pygame.Rect(rect.x - 10, rect.y - 10, rect.width + 20, rect.height + 20)
            pygame.draw.rect(surface, (0, 0, 0), bg)
            pygame.draw.rect(surface, (255, 255, 255), bg, 1)
            surface.blit(text, rect)

    def on_input(self, input_id: str, input_data: Any) -> None:
        if input_id in self.held_keys:
            self.held_keys[input_id] = input_data.pressed or not input_data.released

        if isinstance(input_data, KeyboardData) and not input_data.pressed:
            return
            
        if self.status_text:
            if input_id in ("interact", "enter"):
                if self.bandit.hp <= 0:
                    self.state_machine.pop()
                    if self.on_complete:
                        self.on_complete()
                else:
                    # Retry
                    self.gallagher.x = self.spawn_px
                    self.gallagher.y = self.spawn_py
                    self.bandit.x = self.spawn_bx
                    self.bandit.y = self.spawn_by
                    self.bandit.hp = 3
                    self.bandit.change_state("chase")
                    self.gallagher.change_state("idle")
                    self.bullets.clear()
                    self.status_text = ""
            return
            
        if input_id == "shoot":
            if self.gallagher.state_machine and not isinstance(self.gallagher.state_machine.current, GallagherShoot):
                self.gallagher.change_state("shoot")
