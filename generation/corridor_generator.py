"""
Генератор коридоров между комнатами в BSP-дереве.
"""
import random
from typing import List, Tuple
from generation.bsp_tree import BSPNode
from generation.room_generator import RoomGenerator
from config.generation_config import CORRIDOR_CORNER_PROBABILITY

class CorridorGenerator:
    """
    Создает коридоры между комнатами в BSP-дереве.
    
    Пример использования:
        root = BSPNode(0, 0, 800, 600)
        # ... создание комнат через RoomGenerator ...
        
        corridor_gen = CorridorGenerator()
        corridors = corridor_gen.generate_corridors(root)
    """
    def __init__(
        self,
        room_generator: RoomGenerator,
        corner_probability: float = CORRIDOR_CORNER_PROBABILITY
        ):
        """
        Инициализация генератора коридоров.
        
        Args:
            room_generator: Экземпляр RoomGenerator для поиска комнат
            corner_probability: Вероятность выбора L-образного коридора
        """
        self.room_generator = room_generator
        self.corner_probability = corner_probability

    def generate_corridors(self, node: BSPNode) -> List[Tuple[int, int, int, int]]:
        """
        Генерирует все коридоры в дереве.
        
        Args:
            node: Корневой узел BSP-дерева
            
        Returns:
            Список коридоров в формате (x1, y1, x2, y2)
        """
        corridors = []
        self._generate_corridors_recursive(node, corridors)
        return corridors
    
    def _generate_corridors_recursive(
        self, 
        node: BSPNode, 
        corridors: List[Tuple[int, int, int, int]]
    ) -> None:
        """Рекурсивно генерирует коридоры."""
        if node.left and node.right:
            # Генерация коридоров в поддеревьях
            self._generate_corridors_recursive(node.left, corridors)
            self._generate_corridors_recursive(node.right, corridors)
            
            # Соединение поддеревьев коридором
            self._connect_subtrees(node, corridors)

    def _connect_subtrees(
        self, 
        node: BSPNode, 
        corridors: List[Tuple[int, int, int, int]]
    ) -> None:
        """Создает коридор между левым и правым поддеревом."""
        center_x, center_y = node.get_center()
        
        room_a = self.room_generator.get_room_closest_to(
            node.left, center_x, center_y
        )
        room_b = self.room_generator.get_room_closest_to(
            node.right, center_x, center_y
        )
        
        if room_a and room_b:
            corridor = self._create_corridor_between_rooms(room_a, room_b)
            corridors.extend(corridor)

    def _create_corridor_between_rooms(
        self, 
        room_a: tuple[int, int, int, int],
        room_b: tuple[int, int, int, int]
    ) -> List[Tuple[int, int, int, int]]:
        """
        Создает L-образный коридор между двумя комнатами.
        
        Returns:
            Список из 2 отрезков коридора
        """
        x1 = room_a[0] + room_a[2] // 2
        y1 = room_a[1] + room_a[3] // 2
        x2 = room_b[0] + room_b[2] // 2
        y2 = room_b[1] + room_b[3] // 2
        
        if random.random() < self.corner_probability:
            segments = [(x1, y1, x2, y1), (x2, y1, x2, y2)]
        else:
            segments = [(x1, y1, x1, y2), (x1, y2, x2, y2)]

        return [seg for seg in segments if seg[0] != seg[2] or seg[1] != seg[3]]