import pathlib
from typing import Any

import pygame
from gale.state import StateStack

import settings
from src.entity.Actor import NPC, Player
from src.world.Region import Region


class World:
    def __init__(self, stack: StateStack) -> None:
        self.stack = stack
        map_dir = pathlib.Path(settings.BASE_DIR) / "assets" / "tilemaps"
        self.regions = {
            "center": Region("center"),
            "north": Region("north", map_dir / "museum.json"),
            "east": Region("east", map_dir / "nightclub.json"),
            "west": Region("west", map_dir / "office.json"),
        }
        self.current_region_name = "center"
        self.player = Player(settings.VIRTUAL_WIDTH / 2 - 8, settings.VIRTUAL_HEIGHT / 2 - 10)
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
        self._check_exit()

    def _move_axis(self, dx: float, dy: float) -> None:
        if not dx and not dy:
            return
        next_rect = self.player.rect.move(round(dx), round(dy))
        if self.region.is_walkable(next_rect):
            self.player.x += dx
            self.player.y += dy

    def _check_exit(self) -> None:
        if self.current_region_name != "center":
            return_side = {
                "north": "south",
                "west": "east",
                "east": "west",
            }[self.current_region_name]
            if self.region.at_entry(self.player.rect, return_side):
                self.current_region_name = "center"
                if return_side == "south":
                    self.player.x, self.player.y = self.player.x, 18
                elif return_side == "east":
                    self.player.x, self.player.y = self.region.width - 30, self.player.y
                else:
                    self.player.x, self.player.y = 18, self.player.y
            return

        col = int((self.player.x + 8) // settings.TILE_SIZE)
        row = int((self.player.y + 10) // settings.TILE_SIZE)
        middle_col = self.region.tilemap.cols // 2
        middle_row = self.region.tilemap.rows // 2
        target = None
        spawn = (self.player.x, self.player.y)
        if row <= 0 and abs(col - middle_col) <= 2:
            target, spawn = "north", (self.player.x, self.region.height - 30)
        elif col <= 0 and abs(row - middle_row) <= 2:
            target, spawn = "west", (self.region.width - 30, self.player.y)
        elif col >= self.region.tilemap.cols - 1 and abs(row - middle_row) <= 2:
            target, spawn = "east", (18, self.player.y)

        if target in self.regions:
            target_side = {"north": "south", "west": "east", "east": "west"}[target]
            self.current_region_name = target
            if target == "center":
                self.player.x, self.player.y = spawn
            else:
                self.player.x, self.player.y = self.region.entry_position(target_side)

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
        self.region.render(surface)
        self.player.render(surface)
