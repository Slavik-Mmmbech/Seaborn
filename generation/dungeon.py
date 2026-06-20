import pygame
import random

from typing import List, Tuple
from generation.bsp_tree import BSPNode
from generation.corridor_generator import CorridorGenerator
from generation.room_generator import RoomGenerator
from config.display_config import SCREEN_WIDTH, SCREEN_HEIGHT

class DungeonGenerator:
    """Оркестратор генерации подземелья. Преобразует BSP-дерево в игровую геометрию."""
    def __init__(self, width: int = SCREEN_WIDTH, height: int = SCREEN_HEIGHT, depth: int = 4):
        self.width = width
        self.height = height
        self.depth = depth
        self.root = BSPNode(0, 0, width, height)

    def generate(self) -> Tuple[List[pygame.Rect], List[Tuple[int, int, int, int]]]:
        self.root.recursive_split(self.depth)
        
        room_gen = RoomGenerator()
        room_gen.create_rooms_in_tree(self.root)
        rooms = [pygame.Rect(*n.room) for n in self.root.get_leaf_nodes() if n.room]
        
        corridor_gen = CorridorGenerator(room_generator=room_gen)
        corridors = corridor_gen.generate_corridors(self.root)
        
        return rooms, corridors

    def __repr__(self):
        return f"DUNGEON(root:{self.root}, SIDES:{self.height}/{self.width}, DEPTH:{self.depth})"