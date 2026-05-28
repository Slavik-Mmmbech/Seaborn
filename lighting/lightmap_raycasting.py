import math
from dataclasses import dataclass
from typing import List, Tuple

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

    def __init__(self, grid: List[List[int]], tile_size: int):
        self.grid = grid
        self.tile_size = tile_size
        self.grid_height = len(grid)
        self.grid_width = len(grid[0]) if self.grid_height > 0 else 0

    def compute_visibility_polygon(self, source: LightSource) -> List[Tuple[float, float]]:
        """
        Возвращает упорядоченный список вершин полигона видимости.
        Вход: источник света, радиус, шаг угла, карта препятствий.
        Выход: список координат (x, y) для отрисовки маски освещения.
        """
        polygon_points = []
        current_angle = 0.0
        while current_angle < 2 * math.pi:
            hit_x, hit_y = self._cast_ray(source, current_angle)
            polygon_points.append((hit_x, hit_y))
            current_angle += source.angle_step
            
        # Замыкаю полигон для корректного заполнения
        if polygon_points:
            polygon_points.append(polygon_points[0])
        return polygon_points

    def _cast_ray(self, source: LightSource, angle: float) -> Tuple[float, float]:
        """Выпускает один луч. Возвращает координату столкновения или границы радиуса."""
        dx = math.cos(angle)
        dy = math.sin(angle)
        cx, cy = source.x, source.y
        
        for _ in range(self.MAX_ITERATIONS):
            dist = math.hypot(cx - source.x, cy - source.y)
            if dist >= source.radius:
                return (cx, cy)

            # Перевод мировых координат в индексы сетки
            grid_x = int(cx // self.tile_size)
            grid_y = int(cy // self.tile_size)
            
            if self._is_wall(grid_x, grid_y):
                # Откат на шаг назад, чтобы не провалиться в стену
                return (cx - dx * self.RAYCAST_STEP, cy - dy * self.RAYCAST_STEP)
            
            cx += dx * self.RAYCAST_STEP
            cy += dy * self.RAYCAST_STEP
            
        return (cx, cy)

    def _is_wall(self, gx: int, gy: int) -> bool:
        """Проверка выхода за границы мира или столкновения с препятствием (1)."""
        if 0 <= gx < self.grid_width and 0 <= gy < self.grid_height:
            return self.grid[gy][gx] == 1
        return True