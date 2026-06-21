"""
Модуль бинарного разбиения пространства (BSP - Binary Space Partitioning).

Реализует алгоритм рекурсивного разбиения игрового пространства на 
прямоугольные области для последующей генерации комнат подземелья.
Алгоритм обеспечивает создание непересекающихся комнат
с гарантированными отступами.

Основные компоненты:
    BSPNode: Узел дерева BSP, представляющий прямоугольную область
    Рекурсивное разбиение: O(n) где n - количество узлов дерева

Пример использования:
    >>> root = BSPNode(0, 0, 800, 600)
    >>> root.recursive_split(depth=5)
    >>> leaves = root.get_leaf_nodes()
"""

import random
from typing import List, Optional, Tuple
from config.generation_config import (
    MIN_SIZE,
    MIN_SPLIT,
    SPLIT_RATIO_MIN,
    SPLIT_RATIO_MAX,
    RATIO_LIMIT,
    MIN_NODE_SIZE,
)


class BSPNode:
    """
    Узел дерева бинарного разбиения пространства.

    Attributes:
        x: Координата X левого верхнего угла области
        y: Координата Y левого верхнего угла области
        width: Ширина области в пикселях
        height: Высота области в пикселях
        left: Левый дочерний узел
        right: Правый дочерний узел
        room: Комната (x, y, width, height)

    """

    def __init__(self, x: int, y: int, width: int, height: int):
        self.x: int = x
        self.y: int = y
        self.width: int = width
        self.height: int = height

        self.left: Optional["BSPNode"] = None
        self.right: Optional["BSPNode"] = None
        self.room: Optional[tuple[int, int, int, int]] = None

    def _is_too_small_for_split(self) -> bool:
        """
        Проверка минимального размера для разбиения (принцип KISS).

        Returns:
            bool: True если область слишком мала для разбиения
        """
        return (
            self.width < MIN_NODE_SIZE
            or self.height < MIN_NODE_SIZE
            or self.width < MIN_SIZE
            or self.height < MIN_SIZE
        )

    def split(self) -> bool:
        """
        Разбивает узел на два дочерних узла.

        Определяет оптимальное направление разбиения
        (горизонтальное/вертикальное) на основе соотношения сторон
        и создаёт два дочерних узла.

        Returns:
            bool: True если разбиение успешно, False если область слишком мала
        """
        if self._is_too_small_for_split():
            return False

        split_horizontally = self._determine_split_direction()
        split_pos = self._calculate_split_position(split_horizontally)

        if split_horizontally:
            self._create_horizontal_split(split_pos)
        else:
            self._create_vertical_split(split_pos)

        return True

    def _determine_split_direction(self) -> bool:
        """
        Определяет направление разбиения на основе соотношения сторон.

        Если область значительно шире высоты - разбивает вертикально.
        Если область значительно выше ширины - разбивает горизонтально.
        Иначе выбирает случайное направление.

        Returns:
            bool: True для горизонтального разбиения, False для вертикального
        """
        width_height_ratio = self.width / self.height
        height_width_ratio = self.height / self.width

        if width_height_ratio >= RATIO_LIMIT:
            return False
        elif height_width_ratio >= RATIO_LIMIT:
            return True
        else:
            return random.choice([True, False])

    def _calculate_split_position(self, horizontal: bool) -> int:
        """
        Вычисляет позицию линии разбиения с безопасными границами.
        Гарантирует, что дочерние узлы будут достаточного размера,
        используя процентное соотношение от размера области.

        Args:
            horizontal: Если True, вычисляется позиция по Y, иначе по X

        Returns:
            int: Позиция разбиения относительно начала области

        Note:
            Возвращает середину области как fallback при некорректных расчётах
        """
        size = self.height if horizontal else self.width
        if size <= MIN_SPLIT:
            return size // 2

        min_split = max(1, int(size * SPLIT_RATIO_MIN))
        max_split = min(size - 1, int(size * SPLIT_RATIO_MAX))

        if min_split > max_split:
            return size // 2

        return random.randint(min_split, max_split)

    def _create_horizontal_split(self, split_pos: int) -> None:
        """
        Создаёт горизонтальное разбиение области.

        Args:
            split_pos: Позиция линии разбиения по оси Y (относительно self.y)

        Example:
            # Область 800x600 разбивается на 800x200 и 800x400
            >>> node = BSPNode(0, 0, 800, 600)
            >>> node._create_horizontal_split(200)
            >>> node.left.height, node.right.height
            (200, 400)
        """
        self.left = BSPNode(self.x, self.y, self.width, split_pos)
        self.right = BSPNode(
            self.x, self.y + split_pos, self.width, self.height - split_pos
        )

    def _create_vertical_split(self, split_pos: int) -> None:
        """
        Создаёт вертикальное разбиение области.

        Args:
            split_pos: Позиция линии разбиения по оси X (относительно self.x)

        Example:
            # Область 800x600 разбивается на 300x600 и 500x600
            >>> node = BSPNode(0, 0, 800, 600)
            >>> node._create_vertical_split(300)
            >>> node.left.width, node.right.width
            (300, 500)
        """
        self.left = BSPNode(self.x, self.y, split_pos, self.height)
        self.right = BSPNode(
            self.x + split_pos, self.y, self.width - split_pos, self.height
        )

    def recursive_split(self, depth):
        """
        Рекурсивно разбивает дерево до указанной глубины.

        Применяет алгоритм BSP рекурсивно ко всем дочерним узлам,
        создавая бинарное дерево областей.

        Args:
            depth: Максимальная глубина рекурсии (0 = только корневой узел)

        Complexity:
            O(2^depth) - экспоненциальный рост количества узлов
        """
        if depth <= 0 or not self.split():
            return

        if self.left:
            self.left.recursive_split(depth - 1)
        if self.right:
            self.right.recursive_split(depth - 1)

    def get_leaf_nodes(self) -> List["BSPNode"]:
        """
        Возвращает все листовые узлы дерева.

        Листовые узлы - это узлы без дочерних элементов,
        в которых будут созданы комнаты.

        Returns:
            List[BSPNode]: Список всех листовых узлов

        Complexity:
            O(n) где n - общее количество узлов в дереве
        """
        if self.left is None and self.right is None:
            return [self]

        leaves: List[BSPNode] = []
        if self.left:
            leaves.extend(self.left.get_leaf_nodes())
        if self.right:
            leaves.extend(self.right.get_leaf_nodes())
        return leaves

    def get_center(self) -> tuple[int, int]:
        """Возвращает центр области.

        Returns:
            Tuple[int, int]: Координаты центра (x, y)
        """
        return (self.x + self.width // 2, self.y + self.height // 2)

    def set_room(self, room: Tuple[int, int, int, int]) -> None:
        """
        Устанавливает комнату в узле (принцип инкапсуляции).

        Args:
            room: Кортеж (x, y, width, height) описывающий комнату

        Note:
            Комната должна полностью помещаться в область узла
        """
        self.room = room

    def __repr__(self):
        """Строковое представление узла для отладки."""
        return (f"BSPNode(x={self.x}, y={self.y}, "
                f"w={self.width}, h={self.height})")