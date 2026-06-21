"""
Модуль реализации квадродерева (QuadTree).

Предоставляет структуру данных для иерархического разбиения 2D-пространства.
Используется для оптимизации пространственных запросов,
таких как выборка объектов в области видимости камеры 
или расчет столкновений (Collision Detection).

Алгоритмическая сложность:
    - Вставка (insert): O(log N) в среднем, 
        O(N) в худшем случае (при переполнении)
    - Пространственный запрос (query): O(K + log N), 
        где K — количество найденных объектов
"""

from dataclasses import dataclass
from typing import List, Tuple, Any, Optional, Dict

from config.generation_config import MAX_CAPACITY, MAX_DEPTH, START_DEPTH


@dataclass
class Bounds:
    """
    Прямоугольная область двухмерного пространства.

    Используется для определения границ узлов квадродерева и гео-запросов.

    Attributes:
        x: Левая верхняя координата X.
        y: Левая верхняя координата Y.
        width: Ширина области.
        height: Высота области.
    """

    x: float
    y: float
    width: float
    height: float

    def contains(self, other: "Bounds") -> bool:
        """
        Проверяет, включает ли текущая область другую область полностью.

        Args:
            other: Проверяемый прямоугольник границ объекта.

        Returns:
            True, если объект полностью внутри, иначе False.
        """
        return (
            other.x >= self.x
            and other.y >= self.y
            and other.x + other.width <= self.x + self.width
            and other.y + other.height <= self.y + self.height
        )

    def intersects(self, other: "Bounds") -> bool:
        """
        Проверяет пересечение (наложение) текущей области с другой.

        Args:
            other: Проверяемая область.

        Returns:
            True, если области пересекаются хотя бы частично, иначе False.
        """
        return not (
            other.x > self.x + self.width
            or other.x + other.width < self.x
            or other.y > self.y + self.height
            or other.y + other.height < self.y
        )


class QuadTree:
    """
    Узел квадродерева для пространственного индексирования объектов.

    Реализует паттерн рекурсивного разбиения плоскости на 4 под-квадранта
    при превышении лимита емкости объектов в узле.
    """

    def __init__(
        self,
        bounds: Bounds,
        depth: int = START_DEPTH,
        max_capacity: int = MAX_CAPACITY,
        max_depth: int = MAX_DEPTH,
    ):
        """
        Инициализирует узел квадродерева.

        Args:
            bounds: Геометрические границы, за которые отвечает данный узел.
            depth: Текущая глубина залегания узла в дереве (корень = 0).
            max_capacity: Максимальное количество объектов в узле до деления.
            max_depth: Максимально допустимая глубина дерева.
        """
        self.bounds = bounds
        self.depth = depth
        self.items: List[Tuple[Any, Bounds]] = []
        self.max_capacity = max_capacity
        self.max_depth = max_depth

        # Дочерние квадранты: 0 -> NW, 1 -> NE, 2 -> SW, 3 -> SE
        self.children: List[Optional["QuadTree"]] = [None, None, None, None]

    def insert(self, item: Any, item_bounds: Bounds) -> bool:
        """
        Вставляет объект в структуру дерева.

        Если узел уже разделен, пытается делегировать вставку дочернему узлу.
        Если лимит превышен — запускает процесс деления узла.

        Сложность: O(log N) в среднем.

        Args:
            item: Ссылка на вставляемый игровой объект (например, Entity).
            item_bounds: Прямоугольник коллизии/границ объекта.

        Returns:
            True, если объект успешно интегрирован в структуру дерева, иначе False.
        """
        if not self.bounds.contains(item_bounds):
            return False

        # Если узел уже имеет потомков, вставка делегируется им
        if self.children[0] is not None:
            for child in self.children:
                if child and child.insert(item, item_bounds):
                    return True
            # Объект лежит в границах текущего узла, 
            # но пересекает внутренние границы деления
            self.items.append((item, item_bounds))
            return True

        self.items.append((item, item_bounds))

        # Проверка триггера рекурсивного разбиения узла
        if len(self.items) > self.max_capacity and self.depth < self.max_depth:
            self._subdivide()
        return True

    def query(self, range_bounds: Bounds) -> List[Any]:
        """
        Возвращает все объекты, попадающие в указанную область поиска или пересекающие её.

        Сложность: O(K + log N), где K — размер выборки результатов.

        Args:
            range_bounds: Зона интереса (например, хитбокс камеры или радиус взрыва).

        Returns:
            Список объектов, находящихся в данной области.
        """
        results = []
        if not self.bounds.intersects(range_bounds):
            return results

        # Проверка объектов, хранящихся локально в данном узле
        for item, item_bounds in self.items:
            if range_bounds.intersects(item_bounds):
                results.append(item)

        # Рекурсивный опрос дочерних узлов, если они существуют
        if self.children[0] is not None:
            for child in self.children:
                if child:
                    results.extend(child.query(range_bounds))
        return results

    def _subdivide(self) -> None:
        """
        Разделяет текущий узел на 4 независимых квадранта (NW, NE, SW, SE)
        и перераспределяет локальные объекты между ними.

        Сложность: O(N), где N — текущая емкость узла.
        """
        w_half = self.bounds.width / 2
        h_half = self.bounds.height / 2
        x, y = self.bounds.x, self.bounds.y

        # Индексы: 0 - NorthWest, 1 - NorthEast, 2 - SouthWest, 3 - SouthEast
        self.children[0] = QuadTree(
            Bounds(x, y, w_half, h_half),
            self.depth + 1,
            self.max_capacity,
            self.max_depth,
        )
        self.children[1] = QuadTree(
            Bounds(x + w_half, y, w_half, h_half),
            self.depth + 1,
            self.max_capacity,
            self.max_depth,
        )
        self.children[2] = QuadTree(
            Bounds(x, y + h_half, w_half, h_half),
            self.depth + 1,
            self.max_capacity,
            self.max_depth,
        )
        self.children[3] = QuadTree(
            Bounds(x + w_half, y + h_half, w_half, h_half),
            self.depth + 1,
            self.max_capacity,
            self.max_depth,
        )

        remaining: List[Tuple[Any, Bounds]] = []
        for item, item_bounds in self.items:
            placed = False
            for child in self.children:
                if child and child.bounds.contains(item_bounds):
                    child.insert(item, item_bounds)
                    placed = True
                    break
            if not placed:
                # Оставляем объект на текущем уровне,
                # если он лежит на стыке квадрантов
                remaining.append((item, item_bounds))

        self.items = remaining

    def clear(self) -> None:
        """
        Полностью очищает дерево, уничтожая ссылки на поддеревья.
        Вызывается каждый кадр игрового цикла перед повторным заполнением.

        Сложность: O(N) общего числа узлов.
        """
        self.items.clear()
        if self.children[0] is not None:
            for child in self.children:
                if child:
                    child.clear()
            self.children = [None, None, None, None]

    def get_stats(self) -> Dict[str, Any]:
        """
        Возвращает метрики и статистику текущего узла для отладки производительности.

        Returns:
            Словарь со статистическими параметрами узла дерева.
        """
        return {
            "depth": self.depth,
            "items_count": len(self.items),
            "has_children": self.children[0] is not None,
        }
