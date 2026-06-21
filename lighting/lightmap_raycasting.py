import math
from dataclasses import dataclass
from typing import List, Tuple
from config.enums import TileType
from config.display_config import TILE_SIZE
from config.gameplay_config import RAY_ANGLE_STEP, EPSILON

class GameMap:
    def __init__(self, grid: List[List[int]], grid_height: int, grid_width: int):
        self.grid = grid
        self.grid_height = grid_height
        self.grid_width = grid_width

    def is_wall(self, gx: int, gy: int) -> bool:
        """Проверка выхода за границы мира или столкновения с препятствием."""
        if 0 <= gx < self.grid_width and 0 <= gy < self.grid_height:
            return self.grid[gy][gx] == TileType.WALL
        return True

@dataclass
class LightSource:
    """Параметры динамического источника света."""
    x: float
    y: float
    radius: float
    angle_step: float = RAY_ANGLE_STEP

class Raycaster:
    """
    Алгоритм расчёта видимости (Visibility Polygon) через пошаговое лучепускание.
    Использует DDA (Digital Differential Analyzer) для нахождения пересечений.
    """
    def __init__(self, grid: List[List[int]], tile_size: int = TILE_SIZE):
        self.grid = grid
        self.tile_size = tile_size
        self.grid_height = len(grid)
        self.grid_width = len(grid[0]) if self.grid_height > 0 else 0
        self.game_map = GameMap(self.grid, self.grid_height, self.grid_width)

    def compute_visibility_polygon(self, source: LightSource) -> List[Tuple[float, float]]:
        angles = set()

        for y in range(self.game_map.grid_height):
            for x in range(self.game_map.grid_width):
                if self.game_map.grid[y][x] == TileType.WALL:
                    corners = [
                        (x * self.tile_size, y * self.tile_size),
                        ((x + 1) * self.tile_size, y * self.tile_size),
                        (x * self.tile_size, (y + 1) * self.tile_size),
                        ((x + 1) * self.tile_size, (y + 1) * self.tile_size)
                    ]
                    for wx, wy in corners:
                        ang = math.atan2(wy - source.y, wx - source.x)
                        angles.update([ang - EPSILON, ang, ang + EPSILON])

        sorted_angles = sorted(list(angles))
        polygon_points = []
        
        for ang in sorted_angles:
            hit_x, hit_y = self._cast_ray(source, ang)
            polygon_points.append((hit_x, hit_y))
            
        if polygon_points:
            polygon_points.append(polygon_points[0])
        return polygon_points

    def _cast_ray(self, source: LightSource, angle: float) -> Tuple[float, float]:
        """
        Выпускает один луч с использованием классического алгоритма DDA.
        """
        dx = math.cos(angle)
        dy = math.sin(angle)
        if abs(dx) < 1e-9: dx = 1e-9 * (1 if dx >= 0 else -1)
        if abs(dy) < 1e-9: dy = 1e-9 * (1 if dy >= 0 else -1)

        src_x_tile = source.x / self.tile_size
        src_y_tile = source.y / self.tile_size

        map_x = int(src_x_tile)
        map_y = int(src_y_tile)

        delta_dist_x = abs(1 / dx)
        delta_dist_y = abs(1 / dy)

        if dx > 0:
            step_x = 1
            side_dist_x = (map_x + 1 - src_x_tile) * delta_dist_x
        else:
            step_x = -1
            side_dist_x = (src_x_tile - map_x) * delta_dist_x
            
        if dy > 0:
            step_y = 1
            side_dist_y = (map_y + 1 - src_y_tile) * delta_dist_y
        else:
            step_y = -1
            side_dist_y = (src_y_tile - map_y) * delta_dist_y

        hit = False
        side = 0 

        max_steps = self.grid_width + self.grid_height
        steps_taken = 0

        while not hit and steps_taken < max_steps:
            steps_taken += 1
            
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 0
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 1

            if (map_x < 0 or map_x >= self.grid_width or 
                map_y < 0 or map_y >= self.grid_height):
                hit = True
                break

            if self.game_map.is_wall(map_x, map_y):
                hit = True

        # Вычисление расстояния
        if side == 0:
            perp_wall_dist = side_dist_x - delta_dist_x
        else:
            perp_wall_dist = side_dist_y - delta_dist_y

        hit_x = source.x + perp_wall_dist * dx * self.tile_size
        hit_y = source.y + perp_wall_dist * dy * self.tile_size

        # Ограничение радиусом
        if math.hypot(hit_x - source.x, hit_y - source.y) > source.radius:
            hit_x = source.x + dx * source.radius
            hit_y = source.y + dy * source.radius

        return (hit_x, hit_y)