import pathlib
from typing import Any

import pygame
from gale.camera import Camera
from gale.state import StateStack

import settings
from src.entity.Actor import NPC, Player
from src.world.Region import Region


class World:
    DOOR_TARGETS = ("office", "museum", "nightclub", None, "alley")
    CITY_DOOR_INDEX = {target: index for index, target in enumerate(DOOR_TARGETS) if target}

    def __init__(self, stack: StateStack) -> None:
        self.stack = stack
        map_dir = pathlib.Path(settings.BASE_DIR) / "assets" / "tilemaps"
        self.regions = {
            "city": Region("city", map_dir / "city.json"),
            "museum": Region("museum", map_dir / "museum.json"),
            "nightclub": Region("nightclub", map_dir / "nightclub.json"),
            "office": Region("office", map_dir / "office.json"),
            "alley": Region("alley", map_dir / "alley.json"),
        }
        self.current_region_name = "city"
        city = self.regions["city"]
        self.player = Player(city.width / 2 - 8, city.height / 2 - 10)
        self.camera = Camera(settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT)
        self.camera.follow(self.player, rate=settings.CAMERA_FOLLOW_RATE)
        self._update_camera_bounds()
        self.camera.x, self.camera.y = self.player.x, self.player.y
        self.camera.update(0)
        self._populate_npcs()

    @property
    def region(self) -> Region:
        return self.regions[self.current_region_name]

    def _populate_npcs(self) -> None:
        positions = ((8, 7), (20, 8), (14, 14))
        for region in self.regions.values():
            for index, (col, row) in enumerate(positions):
                x = col * settings.TILE_SIZE + 1
                y = row * settings.TILE_SIZE - 2
                npc = NPC(x, y, ("Mara", "Elias", "June")[index])
                if not region.is_walkable(npc.rect):
                    npc.x, npc.y = self._find_open_position(region, col, row)
                region.npcs.append(npc)

    @staticmethod
    def _find_open_position(region: Region, col: int, row: int) -> tuple[float, float]:
        for radius in range(1, 8):
            for test_col, test_row in (
                (col + radius, row), (col - radius, row),
                (col, row + radius), (col, row - radius),
            ):
                x = test_col * settings.TILE_SIZE + 1
                y = test_row * settings.TILE_SIZE - 2
                if region.is_walkable(pygame.Rect(round(x + 1), round(y - 2), 14, 18)):
                    return x, y
        return col * settings.TILE_SIZE + 1, row * settings.TILE_SIZE - 2

    def update(self, dt: float) -> None:
        dx = float(self.player.held["move_right"] - self.player.held["move_left"])
        dy = float(self.player.held["move_down"] - self.player.held["move_up"])
        if dx and dy:
            dx *= 0.7071
            dy *= 0.7071
        self.player.move(dx, dy)
        self._move_axis(dx * Player.SPEED * dt, 0)
        self._move_axis(0, dy * Player.SPEED * dt)
        self._check_door_collision()
        self.camera.update(dt)

    def _move_axis(self, dx: float, dy: float) -> None:
        if not dx and not dy:
            return
        next_rect = self.player.rect.move(round(dx), round(dy))
        if self.region.is_walkable(next_rect):
            self.player.x += dx
            self.player.y += dy

    def _door_collides(self, door) -> bool:
        return self._door_collides_rect(self.player.rect, door)

    @staticmethod
    def _door_collides_rect(player_rect: pygame.Rect, door) -> bool:
        if not door.width or not door.height:
            return player_rect.collidepoint(round(door.x), round(door.y))
        door_rect = pygame.Rect(
            round(door.x), round(door.y), round(door.width), round(door.height)
        )
        return player_rect.colliderect(door_rect)

    def _check_door_collision(self) -> None:
        for index, door in enumerate(self._door_objects()[:len(self.DOOR_TARGETS)]):
            if not self._door_collides(door):
                continue
            if self.current_region_name == "city":
                target = self.DOOR_TARGETS[index]
                if target is None:
                    return
                self.current_region_name = target
                self.player.x, self.player.y = self.region.entry_position("south")
            else:
                self._return_to_city()
            self._update_camera_bounds()
            return

    def _return_to_city(self) -> None:
        city_door = self.regions["city"].tilemap.object_layers["Doors"][
            self.CITY_DOOR_INDEX[self.current_region_name]
        ]
        door_center = pygame.Vector2(
            city_door.x + city_door.width / 2,
            city_door.y + city_door.height / 2,
        )
        for offset_x, offset_y in (
            (0, 20), (0, -20), (20, 0), (-20, 0),
            (14, 14), (-14, 14), (14, -14), (-14, -14),
        ):
            x = door_center.x + offset_x - 1
            y = door_center.y + offset_y + 2
            player_rect = pygame.Rect(round(x + 1), round(y - 2), 14, 18)
            if (
                self.regions["city"].is_walkable(player_rect)
                and not self._door_collides_rect(player_rect, city_door)
            ):
                self.current_region_name = "city"
                self.player.x, self.player.y = x, y
                return
        raise RuntimeError(f"No walkable spawn found near {self.current_region_name} door")

    def _update_camera_bounds(self) -> None:
        self.camera.bounds = pygame.Rect(0, 0, self.region.width, self.region.height)

    def _door_objects(self):
        return self.region.tilemap.object_layers.get("Doors", [])

    def on_input(self, input_id: str, input_data: Any) -> None:
        self.player.on_input(input_id, input_data)
        if input_id == "interact" and input_data.pressed:
            self._try_interact()

    def _try_interact(self) -> None:
        player_center = self.player.rect.center
        for npc in self.region.npcs:
            if pygame.Vector2(player_center).distance_to(npc.rect.center) <= 30:
                self._clear_movement()
                from src.states.DialogueState import DialogueState

                self.stack.push(DialogueState(self.stack), text=npc.dialogue())
                return

    def _clear_movement(self) -> None:
        for key in self.player.held:
            self.player.held[key] = False

    def render(self, surface: pygame.Surface) -> None:
        self.region.render(surface, self.camera)
        self.player.render(surface, self.camera)
