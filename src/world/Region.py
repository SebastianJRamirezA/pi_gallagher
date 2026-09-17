import pathlib

import pygame
from gale.tilemap import TileMap, load_tiled_map

import settings


class Region:
    def __init__(self, name: str, map_path: pathlib.Path | None = None) -> None:
        self.name = name
        self.npcs = []
        self.triggers = []
        self.map_path = map_path

        if map_path is None:
            self.tilemap = self._create_center()
        else:
            self.tilemap = self._load_json(map_path)

        self.width = self.tilemap.cols * settings.TILE_SIZE
        self.height = self.tilemap.rows * settings.TILE_SIZE

    def _load_json(self, map_path: pathlib.Path) -> TileMap:
        return load_tiled_map(str(map_path))

    def _create_center(self) -> TileMap:
        tilemap = TileMap(settings.TILE_SIZE, settings.TILE_SIZE, settings.TILE_WIDTH, settings.TILE_HEIGHT)
        tilemap.add_tileset(settings.TILESETS["rpg_tileset.tsj"])
        floor = tilemap.add_layer("Floor")
        walls = tilemap.add_layer("Walls")
        floor_tile = 6
        border_tile = 1631
        for row in range(tilemap.rows):
            for col in range(tilemap.cols):
                floor[row][col] = floor_tile
                if row in (0, tilemap.rows - 1) or col in (0, tilemap.cols - 1):
                    walls[row][col] = border_tile

        center_col = tilemap.cols // 2
        center_row = tilemap.rows // 2
        for col in range(center_col - 1, center_col + 2):
            walls[0][col] = 0
        for row in range(center_row - 1, center_row + 2):
            walls[row][0] = 0
            walls[row][tilemap.cols - 1] = 0
        return tilemap

    def _wall_at(self, col: int, row: int) -> bool:
        if not self.tilemap.in_bounds(row, col):
            return True
        for layer_name in self.tilemap.layer_names():
            if layer_name.lower() == "walls":
                return self.tilemap.get_gid(layer_name, row, col) != 0
        return False

    def _floor_at(self, col: int, row: int) -> bool:
        if not self.tilemap.in_bounds(row, col):
            return False
        for layer_name in self.tilemap.layer_names():
            if layer_name.lower() == "floor":
                return self.tilemap.get_gid(layer_name, row, col) != 0
        return True

    def is_walkable(self, rect: pygame.Rect) -> bool:
        left = rect.left // settings.TILE_SIZE
        right = (rect.right - 1) // settings.TILE_SIZE
        top = rect.top // settings.TILE_SIZE
        bottom = (rect.bottom - 1) // settings.TILE_SIZE
        return all(
            self._floor_at(col, row) and not self._wall_at(col, row)
            for row in range(top, bottom + 1)
            for col in range(left, right + 1)
        )

    def _walkable_tile(self, col: int, row: int) -> bool:
        # Construct the candidate foot box (16x16) at tile position
        rect = pygame.Rect(
            col * settings.TILE_SIZE + 1,
            row * settings.TILE_SIZE + 12,
            16,
            16,
        )
        return self.is_walkable(rect)

    def entry_position(self, side: str) -> tuple[float, float]:
        col, row = self._edge_tile(side)
        if side == "museum":
            row += 2
        elif side == "south":
            row -= 2
        elif side == "office":
            col += 2
        else:
            col -= 2

        if not self._walkable_tile(col, row):
            col, row = self._edge_tile(side)

        # Return (x, y) sprite origin corresponding to foot tile collision box
        return col * settings.TILE_SIZE, row * settings.TILE_SIZE
        return self.is_walkable(rect)

    def _edge_tile(self, side: str) -> tuple[int, int]:
        candidates = [
            (col, row)
            for row in range(self.tilemap.rows)
            for col in range(self.tilemap.cols)
            if self._walkable_tile(col, row)
        ]
        center_col = self.tilemap.cols / 2
        center_row = self.tilemap.rows / 2
        if side == "museum":
            return min(candidates, key=lambda tile: (tile[1], abs(tile[0] - center_col)))
        if side == "south":
            return max(candidates, key=lambda tile: (tile[1], -abs(tile[0] - center_col)))
        if side == "office":
            return min(candidates, key=lambda tile: (tile[0], abs(tile[1] - center_row)))
        return max(candidates, key=lambda tile: (tile[0], -abs(tile[1] - center_row)))


    def at_entry(self, player_rect: pygame.Rect, side: str) -> bool:
        col, row = self._edge_tile(side)
        player_col = player_rect.centerx // settings.TILE_SIZE
        player_row = player_rect.centery // settings.TILE_SIZE
        if side == "museum":
            return player_row <= row + 1
        if side == "south":
            return player_row >= row - 1
        if side == "office":
            return player_col <= col + 1
        return player_col >= col - 1

    def render(self, surface: pygame.Surface, camera=None) -> None:
        surface.fill((25, 25, 28))
        self.tilemap.render(surface, camera)
        for npc in self.npcs:
            npc.render(surface, camera)
