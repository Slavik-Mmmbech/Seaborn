"""
Оркестратор генерации подземелья (Dungeon Generator).

Координирует процесс создания подземелья, объединяя:
    - BSP-разбиение пространства
    - Генерацию комнат в листовых узлах
    - Создание коридоров между комнатами

Предоставляет единый интерфейс для генерации полной структуры
подземелья с возвратом списков комнат и коридоров.

Пример использования:
    >>> generator = DungeonGenerator(width=800, height=600, depth=5)
    >>> rooms, corridors = generator.generate()
"""

from typing import List, Tuple, Optional
from generation.bsp_tree import BSPNode
from generation.corridor_generator import CorridorGenerator
from generation.room_generator import RoomGenerator
from config.display_config import SCREEN_WIDTH, SCREEN_HEIGHT
from config.generation_config import DEFAULT_BSP_DEPTH


class DungeonGenerator:
    """
    Оркестратор генерации подземелья.
    
    Преобразует BSP-дерево в игровую геометрию, координируя работу
    генераторов комнат и коридоров.
    
    Attributes:
        width (int): Ширина подземелья в пикселях
        height (int): Высота подземелья в пикселях
        depth (int): Глубина рекурсивного разбиения BSP-дерева
        root (BSPNode): Корневой узел BSP-дерева
        _room_generator (RoomGenerator): Генератор комнат
        _corridor_generator (CorridorGenerator): Генератор коридоров
    
    """

    def __init__(
        self,
        width: int = SCREEN_WIDTH,
        height: int = SCREEN_HEIGHT,
        depth: int = DEFAULT_BSP_DEPTH,
        room_generator: Optional[RoomGenerator] = None,
        corridor_generator: Optional[CorridorGenerator] = None,
    ):
        self.width = width
        self.height = height
        self.depth = depth
        self.root = BSPNode(0, 0, width, height)

        self._room_generator = room_generator or RoomGenerator()

        if corridor_generator is None:
            self._corridor_generator = CorridorGenerator(
                room_provider=self._room_generator
            )
        else:
            self._corridor_generator = corridor_generator

    def generate(
        self,
    ) -> Tuple[List[Tuple[int, int, int, int]], List[Tuple[int, int, int, int]]]:
        """
        Генерирует подземелье.
        
        Выполняет последовательность шагов:
            1. Рекурсивное BSP-разбиение пространства
            2. Создание комнат в листовых узлах
            3. Сбор списка всех комнат
            4. Создание коридоров между комнатами
        
        Returns:
            Tuple[List[Tuple[int * 4], List[Tuple[int * 4]]]:
                - rooms: Список комнат в формате (x, y, width, height)
                - corridors: Список коридоров в формате (x1, y1, x2, y2)
        """
        self.root.recursive_split(self.depth)

        # 2. Создание комнат
        self._room_generator.create_rooms_in_tree(self.root)

        # 3. Сбор результатов
        rooms = [n.room for n in self.root.get_leaf_nodes() if n.room]

        # 4. Создание коридоров
        corridors = self._corridor_generator.generate_corridors(self.root)

        return rooms, corridors

    def __repr__(self):
        """Строковое представление генератора для отладки."""
        return (
            f"DUNGEON(root:{self.root},"
            f"SIDES:{self.height}/{self.width},"
            f"DEPTH:{self.depth})"
        )
