"""
Модуль для бинарного разбиения пространства (BSP).
Отвечает за структуру дерева и разбиение.
"""
import random
from typing import List, Optional
from config.generation_config import MIN_SIZE, SPLIT_RATIO_MIN, SPLIT_RATIO_MAX, RATIO_LIMIT

class BSPNode:
    """
    Узел дерева BSP.
    
    Attributes:
        x, y: Координаты левого верхнего угла
        width, height: Размеры области
        left, right: Дочерние узлы
        room: Комната (x, y, width, height), если это лист
    """
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x: int = x
        self.y: int = y
        self.width: int = width
        self.height: int = height

        self.left: Optional['BSPNode'] = None
        self.right: Optional['BSPNode'] = None
        self.room: Optional[tuple[int, int, int, int]] = None   

    def split(self) -> bool:
        """
        Разбивает текущий узел на два дочерних.
        
        Returns:
            True если разбиение успешно, False если область слишком мала
        """ 
        if self.width < MIN_SIZE or self.height < MIN_SIZE:
            return False

        split_horizontally = self._determine_split_direction()

        split_pos = self._calculate_split_position(split_horizontally)

        if split_horizontally:
            self._create_horizontal_split(split_pos)
        else:
            self._create_vertical_split(split_pos)

        return True

    def _determine_split_direction(self) -> bool:
        """Определяет, делить ли горизонтально (True) или вертикально (False)."""
        width_height_ratio = self.width / self.height
        height_width_ratio = self.height / self.width
        
        if width_height_ratio >= RATIO_LIMIT:
            return False
        elif height_width_ratio >= RATIO_LIMIT:
            return True
        else:
            return random.choice([True, False])
        
    def _calculate_split_position(self, horizontal: bool) -> int:
        """Вычисляет позицию разбиения с безопасными границами.

        Гарантируем, что возвращаемая позиция лежит в диапазоне [1, size-1].
        При некорректных расчетах возвращаем середину области в качестве
        безопасного фоллбэка.
        """
        size = self.height if horizontal else self.width
        if size <= 2:
            return size // 2

        min_split = max(1, int(size * SPLIT_RATIO_MIN))
        max_split = min(size - 1, int(size * SPLIT_RATIO_MAX))

        if min_split > max_split:
            return size // 2

        return random.randint(min_split, max_split)
    
    def _create_horizontal_split(self, split_pos: int) -> None:
        """Создает горизонтальное разбиение."""
        self.left = BSPNode(
            self.x, self.y,
            self.width, split_pos
        )
        self.right = BSPNode(
            self.x, self.y + split_pos,
            self.width, self.height - split_pos
        )
        
    def _create_vertical_split(self, split_pos: int) -> None:
        """Создает вертикальное разбиение."""
        self.left = BSPNode(
            self.x, self.y,
            split_pos, self.height
            )
        self.right = BSPNode(
            self.x + split_pos, self.y,
            self.width - split_pos, self.height
            )
        
    def recursive_split(self, depth):
        """Рекурсивно разбивает дерево до указанной глубины."""
        if depth <= 0 or not self.split():
            return
        
        if self.left:
            self.left.recursive_split(depth - 1)
        if self.right:
            self.right.recursive_split(depth - 1)

    def get_leaf_nodes(self) -> List['BSPNode']:
        """Возвращает все листовые узлы дерева."""
        if self.left is None and self.right is None:
            return [self]
        
        leaves: List[BSPNode] = []
        if self.left:
            leaves.extend(self.left.get_leaf_nodes())
        if self.right:
            leaves.extend(self.right.get_leaf_nodes())
        return leaves

    def get_center(self) -> tuple[int, int]:
        """Возвращает центр области."""
        return (
            self.x + self.width // 2,
            self.y + self.height // 2
        )    

    def __repr__(self):
        return f"BSP TREE(CORDS:{self.x}/{self.y}, SIDES:{self.height}/{self.width})"