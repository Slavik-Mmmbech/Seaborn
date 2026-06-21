"""
Генератор коридоров между комнатами в BSP-дереве.

Реализует алгоритм соединения комнат коридорами на основе структуры BSP-дерева:
    - Соединение соседних поддеревьев
    - Создание L-образных коридоров с вероятностным выбором поворота
    - Использование RoomProvider для поиска ближайших комнат

Алгоритмические характеристики:
    - Генерация всех коридоров: O(n) где n - количество узлов
    - Создание коридора между комнатами: O(1)
    - Поиск комнат для соединения: O(log n) в среднем

Пример использования:
    >>>  corridor_gen = CorridorGenerator(
    ...     room_provider=room_gen, corner_probability=0.5
    ... )
    >>> corridors = corridor_gen.generate_corridors(root)
"""

import random
from typing import List, Tuple, Protocol, Optional
from generation.bsp_tree import BSPNode
from config.generation_config import CORRIDOR_CORNER_PROBABILITY
from config.logging_config import setup_logger

logger = setup_logger(__name__)


class RoomProvider(Protocol):
    """
    Интерфейс поставщика комнат (принцип Dependency Inversion - SOLID).
    
    Определяет контракт для классов, предоставляющих доступ к комнатам
    в BSP-дереве. Позволяет использовать различные реализации генераторов
    комнат без изменения кода CorridorGenerator.
    """

    def get_room_closest_to(self, node: BSPNode, x: int, y: int) -> Optional[Tuple]:
        """Находит ближайшую комнату к точке."""
        pass

    def get_random_room(self, node: BSPNode) -> Optional[Tuple]:
        """Возвращает случайную комнату из поддерева."""
        pass


class CorridorGenerator:
    """
    Генератор коридоров между комнатами BSP-дерева.
    
    Создаёт коридоры рекурсивно, соединяя комнаты из левого и правого
    поддеревьев каждого узла. Использует L-образные коридоры с 
    вероятностным выбором направления поворота.
    
    Attributes:
        room_provider (RoomProvider): Поставщик комнат для поиска
        corner_probability (float): Вероятность выбора L-образного 
                                    коридора (0.0-1.0)
    
    Example:
        >>> generator = CorridorGenerator(
        ...     room_provider=room_generator,
        ...     corner_probability=0.7
        ... )
        >>> corridors = generator.generate_corridors(root_node)
    """

    def __init__(
        self,
        room_provider: RoomProvider,
        corner_probability: float = CORRIDOR_CORNER_PROBABILITY,
    ):
        self.room_provider = room_provider
        self.corner_probability = corner_probability

    def generate_corridors(self, node: BSPNode) -> List[Tuple[int, int, int, int]]:
        """
        Генерирует все коридоры в дереве.
        
        Запускает рекурсивный обход дерева для создания коридоров
        между всеми соседними поддеревьями.
        
        Args:
            node: Корневой узел BSP-дерева
            
        Returns:
            List[Tuple[int, int, int, int]]: Список коридоров в формате
                (x1, y1, x2, y2) где (x1,y1) и (x2,y2) - конечные точки
        """
        corridors = []
        self._generate_corridors_recursive(node, corridors)
        return corridors

    def _generate_corridors_recursive(
        self, node: BSPNode, corridors: List[Tuple[int, int, int, int]]
    ) -> None:
        """
        Рекурсивно генерирует коридоры в поддеревьях.
        
        Алгоритм:
            1. Рекурсивно создаёт коридоры в левом поддереве
            2. Рекурсивно создаёт коридоры в правом поддереве
            3. Соединяет левое и правое поддеревья коридором
        
        Args:
            node: Текущий узел дерева
            corridors: Список для добавления сгенерированных коридоров
            
        Note:
            Коридоры создаются только в узлах с двумя детьми
        """
        if node.left and node.right:
            # Генерация коридоров в поддеревьях
            self._generate_corridors_recursive(node.left, corridors)
            self._generate_corridors_recursive(node.right, corridors)

            # Соединение поддеревьев коридором
            self._connect_subtrees(node, corridors)

    def _connect_subtrees(
        self, node: BSPNode, corridors: List[Tuple[int, int, int, int]]
    ) -> None:
        """
        Создаёт коридор между левым и правым поддеревом.
        
        Находит ближайшую к центру узла комнату в каждом поддереве
        и соединяет их коридором.
        
        Args:
            node: Узел дерева с двумя поддеревьями
            corridors: Список для добавления коридора
            
        Note:
            Использует центр узла как точку для поиска ближайших комнат
        """
        center_x, center_y = node.get_center()

        if not node.left or not node.right:
            logger.warning(f"Узел без поддеревьев: {node}")
            return

        # Поиск ближайших комнат в каждом поддереве
        room_a = self.room_provider.get_room_closest_to(
                node.left, center_x, center_y
        )
        room_b = self.room_provider.get_room_closest_to(
                node.right, center_x, center_y
        )

        if not room_a or not room_b:
            logger.warning(
                f"Не удалось соединить поддеревья:"
                f"room_a={room_a}, room_b={room_b}"
            )
            return

        # Создание коридора между комнатами
        corridor = self._create_corridor_between_rooms(room_a, room_b)
        corridors.extend(corridor)

    def _create_corridor_between_rooms(
        self, room_a: tuple[int, int, int, int], room_b: tuple[int, int, int, int]
    ) -> List[Tuple[int, int, int, int]]:
        """
        Создаёт L-образный коридор между двумя комнатами.
        
        Соединяет центры комнат двумя отрезками:
            - Вертикальный + горизонтальный, или
            - Горизонтальный + вертикальный
        
        Выбор направления определяется corner_probability.
        
        Args:
            room_a: Первая комната (x, y, width, height)
            room_b: Вторая комната (x, y, width, height)
            
        Returns:
            List[Tuple[int, int, int, int]]: Список из 1-2 отрезков коридора
                в формате (x1, y1, x2, y2)
        """
        # Центры комнат
        x1 = room_a[0] + room_a[2] // 2
        y1 = room_a[1] + room_a[3] // 2
        x2 = room_b[0] + room_b[2] // 2
        y2 = room_b[1] + room_b[3] // 2

        # Выбор формы коридора (L-образный с поворотом)
        if random.random() < self.corner_probability:
             # Сначала горизонтально, потом вертикально
            segments = [(x1, y1, x2, y1), (x2, y1, x2, y2)]
        else:
            # Сначала вертикально, потом горизонтально
            segments = [(x1, y1, x1, y2), (x1, y2, x2, y2)]

        # Фильтрация нулевых отрезков
        return [
            seg for seg in segments
            if seg[0] != seg[2] or seg[1] != seg[3]
            ]
