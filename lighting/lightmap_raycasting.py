import math
from dataclasses import dataclass
from typing import List, Tuple
from enum import IntEnum

from config.display_config import TILE_SIZE
from config.gameplay_config import FULL_CIRCLE

class TileType(IntEnum):
    FLOOR = 0
    WALL = 1

class GameMap:
    def __init__(self, grid: List[List[int]], grid_height: int, grid_width: int):
        self.grid = grid
        self.grid_height = grid_height
        self.grid_width = grid_width

    def _is_wall(self, gx: int, gy: int) -> bool:
        """Проверка выхода за границы мира или столкновения с препятствием (1)."""
        if 0 <= gx < self.grid_width and 0 <= gy < self.grid_height:
            return self.grid[gy][gx] == TileType.WALL
        return True

@dataclass
class LightSource:
    """Параметры динамического источника света."""
    x: float
    y: float
    radius: float
    angle_step: float = math.radians(5.0)  # ~72 луча на полный круг

class Raycaster:
    """
    Алгоритм расчёта видимости (Visibility Polygon) через пошаговое лучепускание.
    """
    RAYCAST_STEP: float = 1.0
    MAX_ITERATIONS: int = 5000  # Защита от зависания при некорректных данных

    def __init__(self, grid: List[List[int]], tile_size: int = TILE_SIZE):
        self.grid = grid
        self.tile_size = tile_size
        self.grid_height = len(grid)
        self.grid_width = len(grid[0]) if self.grid_height > 0 else 0
        self.game_map = GameMap(self.grid, self.grid_height, self.grid_width)

    def compute_visibility_polygon(self, source: LightSource) -> List[Tuple[float, float]]:
        angles = set()
        EPS = 0.0001
        
        # 1. Сбор углов стен
        for y in range(self.game_map.grid_height):
            for x in range(self.game_map.grid_width):
                if self.game_map.grid[y][x] == TileType.WALL:
                    # 4 угла тайла
                    corners = [
                        (x * self.tile_size, y * self.tile_size),
                        ((x + 1) * self.tile_size, y * self.tile_size),
                        (x * self.tile_size, (y + 1) * self.tile_size),
                        ((x + 1) * self.tile_size, (y + 1) * self.tile_size)
                    ]
                    for wx, wy in corners:
                        ang = math.atan2(wy - source.y, wx - source.x)
                        angles.update([ang - EPS, ang, ang + EPS])


        sorted_angles = sorted(angles)
        polygon_points = []
        
        for ang in sorted_angles:
            # Нормализуем угол в [0, 2π)
            ang = ang % FULL_CIRCLE
            hit_x, hit_y = self._cast_ray(source, ang)
            polygon_points.append((hit_x, hit_y))
            
        # Замыкаем полигон
        if polygon_points:
            polygon_points.append(polygon_points[0])
        return polygon_points

    def _cast_ray(self, source: LightSource, angle: float) -> Tuple[float, float]:
        """Выпускает один луч с использованием алгоритма DDA."""
        dx = math.cos(angle)
        dy = math.sin(angle)

        cx, cy = source.x, source.y

        step_x = 1 if dx > 0 else -1
        step_y = 1 if dy > 0 else -1
        
        # 2. Текущие индексы тайла
        grid_x = int(cx // self.tile_size)
        grid_y = int(cy // self.tile_size)
        
        delta_dist_x = abs(self.tile_size / dx) if dx != 0 else float('inf')
        delta_dist_y = abs(self.tile_size / dy) if dy != 0 else float('inf')
        
        if dx > 0:
            side_dist_x = ((grid_x + 1) * self.tile_size - cx) / abs(dx)
        else:
            side_dist_x = (cx - grid_x * self.tile_size) / abs(dx) if dx != 0 else float('inf')
            
        if dy > 0:
            side_dist_y = ((grid_y + 1) * self.tile_size - cy) / abs(dy)
        else:
            side_dist_y = (cy - grid_y * self.tile_size) / abs(dy) if dy != 0 else float('inf')

        while True:
            if not (0 <= grid_x < self.game_map.grid_width and 0 <= grid_y < self.game_map.grid_height):
                return (cx, cy)
            
            if math.hypot(cx - source.x, cy - source.y) < 0.1:
                # Делаем первый прыжок без проверки стены
                if side_dist_x < side_dist_y:
                    side_dist_x += delta_dist_x
                    grid_x += step_x
                    cx = grid_x * self.tile_size if step_x > 0 else (grid_x + 1) * self.tile_size
                else:
                    side_dist_y += delta_dist_y
                    grid_y += step_y
                    cy = grid_y * self.tile_size if step_y > 0 else (grid_y + 1) * self.tile_size
                continue
            
            dist = math.hypot(cx - source.x, cy - source.y)
            if dist >= source.radius:
                return (cx, cy)
            
            if self.game_map._is_wall(grid_x, grid_y):
                return (cx, cy)
            
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                grid_x += step_x
                cx = grid_x * self.tile_size if step_x > 0 else (grid_x + 1) * self.tile_size

            else:
                side_dist_y += delta_dist_y
                grid_y += step_y
                cy = grid_y * self.tile_size if step_y > 0 else (grid_y + 1) * self.tile_size
