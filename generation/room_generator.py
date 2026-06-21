"""
Генератор комнат в BSP-дереве.

Отвечает за создание комнат в листовых узлах BSP-дерева с учётом:
    - Минимальных отступов от границ области
    - Ограничений соотношения сторон комнат
    - Гарантированного размещения внутри выделенной области

Пример использования:
    >>> root = BSPNode(0, 0, 800, 600)
    >>> root.recursive_split(depth=5)
    >>> generator = RoomGenerator()
    >>> generator.create_rooms_in_tree(root)
"""

import random
import math
from generation.bsp_tree import BSPNode
from config.generation_config import (
    ROOM_MARGIN,
    ROOM_DELTA,
    ROOM_MIN_FILL,
    MAX_ASPECT_RATIO,
    ROOM_SIZE_OFFSET,
)
from typing import Optional, Tuple


class RoomGenerator:
    """
    Генератор комнат в листовых узлах BSP-дерева.

    Создаёт комнаты с контролируемыми параметрами:
        - Размер относительно области (min_fill_ratio)
        - Отступы от границ (ROOM_MARGIN, ROOM_OFFSET)
        - Соотношение сторон (MAX_ASPECT_RATIO)

    Attributes:
        min_fill_ratio (float): Минимальный размер комнаты относительно
                                области узла (0.0-1.0)
    """

    def __init__(self, min_fill_ratio: float = ROOM_MIN_FILL):
        self.min_fill_ratio = min_fill_ratio

    def _calculate_dimension(self, size: int, margin: int) -> int:
        """
        Рассчитывает размер комнаты с учётом отступов.
        Выбирает случайный размер в диапазоне [min_size, max_size] где:
            - min_size = size * min_fill_ratio
            - max_size = size - margin

        Args:
            size: Размер области узла
            margin: Минимальный отступ от границы

        Returns:
            int: Размер комнаты
        """
        min_size = max(1, int(size * self.min_fill_ratio))
        max_size = size - margin
        return min_size if max_size < min_size else random.randint(
            min_size, max_size
        )

    def _calculate_position(
        self, node_start: int, node_size: int, room_size: int, offset: int
    ) -> int:
        """ "
        Вычисляет позицию комнаты с учётом отступов.
        Позиция выбирается случайно в допустимом диапазоне так,
        чтобы комната полностью помещалась в область узла.

        Args:
            node_start: Начало области узла (x или y)
            node_size: Размер области узла
            room_size: Размер комнаты
            offset: Отступ от границы области

        Returns:
            int: Координата начала комнаты
        """
        min_pos = node_start + offset
        max_pos = node_start + node_size - room_size - offset
        return min_pos if max_pos <= min_pos else random.randint(
            min_pos, max_pos
        )

    def _normalize_aspect_ratio(self, width: int, height: int) -> Tuple[int, int]:
        """
        Ограничивает соотношение сторон комнаты.

        Предотвращает создание слишком узких или высоких комнат,
        ограничивая соотношение сторон значением MAX_ASPECT_RATIO.

        Args:
            width: Ширина комнаты
            height: Высота комнаты

        Returns:
            Tuple[int, int]: Нормализованные (width, height)
        """
        if width / height > MAX_ASPECT_RATIO:
            width = int(height * MAX_ASPECT_RATIO)
        elif height / width > MAX_ASPECT_RATIO:
            height = int(width * MAX_ASPECT_RATIO)
        return width, height

    def create_rooms_in_tree(self, node: BSPNode) -> None:
        """
        Создаёт комнаты во всех листовых узлах дерева.

        Рекурсивно обходит дерево и создаёт комнаты только в листовых узлах
        (узлах без дочерних элементов).

        Args:
            node: Корневой узел BSP-дерева
        """
        if node.left is None and node.right is None:
            self._create_room_in_node(node)
        else:
            if node.left:
                self.create_rooms_in_tree(node.left)
            if node.right:
                self.create_rooms_in_tree(node.right)

    def _create_room_in_node(self, node: BSPNode) -> None:
        """
        Создаёт комнату в одном листовом узле.

        Алгоритм:
            1. Рассчитывает размеры комнаты с отступами
            2. Нормализует соотношение сторон
            3. Вычисляет позицию с отступами
            4. Проверяет границы
            5. Устанавливает комнату в узел

        Args:
            node: Листовой узел BSP-дерева

        Note:
            Использует инкапсуляцию через node.set_room()
        """
        # Расчёт размеров с отступами
        room_width = self._calculate_dimension(node.width, ROOM_MARGIN)
        room_height = self._calculate_dimension(node.height, ROOM_MARGIN)

        # Нормализация соотношения сторон
        room_width, room_height = self._normalize_aspect_ratio(
            room_width, room_height
        )

        # Позиционирование
        room_x = self._calculate_position(
            node.x, node.width, room_width, ROOM_SIZE_OFFSET
        )
        room_y = self._calculate_position(
            node.y, node.height, room_height, ROOM_SIZE_OFFSET
        )

        # Финальная проверка границ
        room_width = min(room_width, node.width - (room_x - node.x) - ROOM_DELTA)
        room_height = min(room_height, node.height - (room_y - node.y) - ROOM_DELTA)

        # Инкапсуляция через метод узла
        node.set_room((room_x, room_y, room_width, room_height))

    def get_room_closest_to(
        self, node: BSPNode, x: int, y: int
    ) -> Optional[Tuple[int, int, int, int]]:
        """
        Находит комнату в поддереве, ближайшую к указанной точке.
        Рекурсивно обходит поддерево и вычисляет расстояние от центров
        комнат до целевой точки, возвращая ближайшую.

        Args:
            node: Корневой узел поддерева для поиска
            x: Координата X целевой точки
            y: Координата Y целевой точки

        Returns:
            Optional[Tuple[int, int, int, int]]: Ближайшая комната
                (x, y, width, height) или None если комнат нет
        """
        if node.room:
            return node.room

        best_room = None
        min_dist = float("inf")

        children = []
        if node.left:
            children.append(node.left)
        if node.right:
            children.append(node.right)

        for child in children:
            candidate = self.get_room_closest_to(child, x, y)
            if candidate:
                # Вычисляем центр комнаты
                cx = candidate[0] + candidate[2] // 2
                cy = candidate[1] + candidate[3] // 2

                dist = math.hypot(cx - x, cy - y)

                if dist < min_dist:
                    min_dist = dist
                    best_room = candidate

        return best_room

    def get_random_room(self, node: BSPNode) -> Optional[tuple[int, int, int, int]]:
        """
        Возвращает случайную комнату из поддерева.

        Args:
            node: Корневой узел поддерева

        Returns:
            Optional[Tuple[int, int, int, int]]: Случайная комната
                или None если комнат нет
        """
        if node.room:
            return node.room

        rooms = []
        if node.left:
            room = self.get_random_room(node.left)
            if room:
                rooms.append(room)

        if node.right:
            room = self.get_random_room(node.right)
            if room:
                rooms.append(room)

        return random.choice(rooms) if rooms else None
