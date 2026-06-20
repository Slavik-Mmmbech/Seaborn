"""
Генератор комнат в BSP-дереве.
Отвечает за создание комнат в листовых узлах.
"""
import random
from generation.bsp_tree import BSPNode
from config.generation_config import ROOM_MARGIN, ROOM_OFFSET, ROOM_MIN_FILL
from typing import Optional, Tuple

class RoomGenerator:
    """
    Генерирует комнаты в листовых узлах BSP-дерева.
    
    Пример использования:
        root = BSPNode(0, 0, 800, 600)
        root.recursive_split(depth=5)
        
        generator = RoomGenerator()
        generator.create_rooms_in_tree(root)
    """
    def __init__(self, min_fill_ratio: float = ROOM_MIN_FILL):
        """
        Инициализация генератора.
        
        Args:
            min_fill_ratio: Минимальный размер комнаты относительно области (0.0-1.0)
        """
        self.min_fill_ratio = min_fill_ratio
        
    def create_rooms_in_tree(self, node: BSPNode) -> None:
        """
        Создает комнаты во всех листовых узлах дерева.
        
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
        """Создает комнату в одном узле."""
        # Width/height: ensure min/max are valid integers
        min_w = max(1, int(node.width * self.min_fill_ratio))
        max_w = max(min_w, node.width - ROOM_MARGIN)
        if max_w <= min_w:
            room_width = min_w
        else:
            room_width = random.randint(min_w, max_w)

        min_h = max(1, int(node.height * self.min_fill_ratio))
        max_h = max(min_h, node.height - ROOM_MARGIN)
        if max_h <= min_h:
            room_height = min_h
        else:
            room_height = random.randint(min_h, max_h)

        # Position: if there is no space for randomness, fall back to the minimum offset
        min_x = node.x + ROOM_OFFSET
        max_x = node.x + node.width - room_width - ROOM_OFFSET
        if max_x <= min_x:
            room_x = min_x
        else:
            room_x = random.randint(min_x, max_x)

        min_y = node.y + ROOM_OFFSET
        max_y = node.y + node.height - room_height - ROOM_OFFSET
        if max_y <= min_y:
            room_y = min_y
        else:
            room_y = random.randint(min_y, max_y)

        node.room = (room_x, room_y, room_width, room_height)

    def get_room_closest_to(self, node: BSPNode,  target_x: int, target_y: int) -> Optional[Tuple[int, int, int, int]]:
        """
        Находит комнату в поддереве, ближайшую к указанной точке.
        
        Args:
            node: Корневой узел поддерева для поиска
            target_x, target_y: Целевые координаты
            
        Returns:
            Комната (x, y, width, height) или None
        """
        if node.room:
            return node.room

        best_room = None
        min_dist = float('inf')

        children = []
        if node.left: children.append(node.left)
        if node.right: children.append(node.right)

        for child in children:
            candidate = self.get_room_closest_to(child, target_x, target_y)
            if candidate:
                cx = candidate[0] + candidate[2] // 2
                cy = candidate[1] + candidate[3] // 2

                dist = abs(cx - target_x) + abs(cy - target_y)
                
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
            Случайная комната или None
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
