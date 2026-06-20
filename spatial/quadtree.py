from dataclasses import dataclass
from typing import List, Tuple, Any, Optional

from config.generation_config import MAX_CAPACITY, MAX_DEPTH

@dataclass
class Bounds:
    """Прямоугольная область пространства. Используется для гео-запросов."""
    x: float
    y: float
    width: float
    height: float

    def contains(self, other: 'Bounds') -> bool:
        return (other.x >= self.x and other.y >= self.y and
                other.x + other.width <= self.x + self.width and
                other.y + other.height <= self.y + self.height)

    def intersects(self, other: 'Bounds') -> bool:
        return not (other.x > self.x + self.width or
                    other.x + other.width < self.x or
                    other.y > self.y + self.height or
                    other.y + other.height < self.y)

class QuadTree:
    """
    Иерархическое разбиение 2D-пространства.
    """
    MAX_CAPACITY = MAX_CAPACITY
    MAX_DEPTH = MAX_DEPTH

    def __init__(self, bounds: Bounds,
                 depth: int = 0,
                 max_capacity: int = MAX_CAPACITY,
                 max_depth: int = MAX_DEPTH
                 ):
        self.bounds = bounds
        self.depth = depth
        self.items: List[Tuple[Any, Bounds]] = []
        self.max_capacity = max_capacity
        self.max_depth = max_depth
        self.children: List[Optional['QuadTree']] = [None, None, None, None]

    def insert(self, item: Any, item_bounds: Bounds) -> bool:
        """Вставляет объект, если его границы полностью лежат в пределах узла."""
        if not self.bounds.contains(item_bounds):
            return False

        # Если узел разделён, вставка делегируется дочерним
        if self.children[0] is not None:
            for child in self.children:
                if child.insert(item, item_bounds):
                    return True
            # Если объект не помещается полностью в дочерние квадранты,
            # храним его в текущем узле вместо отбрасывания.
            self.items.append((item, item_bounds))
            return True

        self.items.append((item, item_bounds))
        # Превышение ёмкости → рекурсивное разбиение
        if len(self.items) > self.max_capacity and self.depth < self.max_depth:
            self._subdivide()
        return True

    def query(self, range_bounds: Bounds) -> List[Any]:
        """Возвращает все объекты, пересекающие заданную область."""
        results = []
        if not self.bounds.intersects(range_bounds):
            return results

        # Проверка локальных объектов
        for item, item_bounds in self.items:
            if range_bounds.intersects(item_bounds):
                results.append(item)

        # Рекурсивный обход дочерних узлов
        if self.children[0] is not None:
            for child in self.children:
                results.extend(child.query(range_bounds))
        return results

    def _subdivide(self) -> None:
        """Разделяет текущий узел на 4 квадранта и распределяет объекты."""
        w_half = self.bounds.width / 2
        h_half = self.bounds.height / 2
        x, y = self.bounds.x, self.bounds.y

        self.children[0] = QuadTree(Bounds(x, y, w_half, h_half), self.depth + 1)
        self.children[1] = QuadTree(Bounds(x + w_half, y, w_half, h_half), self.depth + 1)
        self.children[2] = QuadTree(Bounds(x, y + h_half, w_half, h_half), self.depth + 1)
        self.children[3] = QuadTree(Bounds(x + w_half, y + h_half, w_half, h_half), self.depth + 1)

        # Переносим существующие объекты в дочерние узлы
        remaining: List[Tuple[Any, Bounds]] = []
        for item, item_bounds in self.items:
            placed = False
            for child in self.children:
                if child.bounds.contains(item_bounds):
                    child.insert(item, item_bounds)
                    placed = True
                    break
            if not placed:
                # Оставляем объекты, которые не умещаются полностью ни в одном дочернем квадранте
                remaining.append((item, item_bounds))

        self.items = remaining

    def clear(self) -> None:
        """Сброс дерева. Вызывается каждый кадр при обновлении позиций сущностей."""
        self.items.clear()
        if self.children[0] is not None:
            for child in self.children:
                child.clear()
            self.children = [None, None, None, None]
