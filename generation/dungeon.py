import pygame
import random
from typing import List, Tuple
from generation.bsp_tree import BSPNode
from config import SCREEN_WIDTH, SCREEN_HEIGHT

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
        corridors = self._build_corridors(self.root)
        return rooms, corridors

    @staticmethod
    def _safe_random_point(node: BSPNode, margin: int = 4) -> Tuple[int, int]:
        """Возвращает случайную точку внутри узла с защитой от выхода за границы."""
        safe_w = max(node.width, margin * 2 + 1)
        safe_h = max(node.height, margin * 2 + 1)
        x = random.randint(node.x + margin, node.x + safe_w - margin)
        y = random.randint(node.y + margin, node.y + safe_h - margin)
        return x, y

    def _build_corridors(self, node: BSPNode) -> List[Tuple[int, int, int, int]]:
        """Рекурсивно строит L-образные коридоры между поддеревами."""
        corridors: List[Tuple[int, int, int, int]] = []
        
        if node.left and node.right:
            corridors.extend(self._build_corridors(node.left))
            corridors.extend(self._build_corridors(node.right))
            
            left_leaves = node.left.get_leaf_nodes()
            right_leaves = node.right.get_leaf_nodes()
            
            if left_leaves and right_leaves:
                l_room = random.choice(left_leaves)
                r_room = random.choice(right_leaves)
                
                p1 = self._safe_random_point(l_room)
                p2 = self._safe_random_point(r_room)
                
                # Случайный порядок поворота (L или Г)
                if random.choice([True, False]):
                    corridors.append((p1[0], p1[1], p2[0], p1[1]))  # горизонталь
                    corridors.append((p2[0], p1[1], p2[0], p2[1]))  # вертикаль
                else:
                    corridors.append((p1[0], p1[1], p1[0], p2[1]))  # вертикаль
                    corridors.append((p1[0], p2[1], p2[0], p2[1]))  # горизонталь
                    
        return corridors