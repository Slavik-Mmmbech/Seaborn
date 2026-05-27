import pytest
from collections import deque
from generation.bsp_tree import BSPNode
from generation.room_generator import RoomGenerator
from generation.corridor_generator import CorridorGenerator
from config import SCREEN_WIDTH, SCREEN_HEIGHT

class TestDungeonIntegration:
    """Интеграционные тесты полного пайплайна генерации подземелья."""

    def _generate_full_dungeon(self, depth: int = 4):
        """Вспомогательный метод: запускает полный цикл генерации."""
        root = BSPNode(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        root.recursive_split(depth=depth)
        
        room_gen = RoomGenerator(min_fill_ratio=0.5)
        room_gen.create_rooms_in_tree(root)
        
        corridor_gen = CorridorGenerator(room_generator=room_gen, corner_probability=0.5)
        corridors = corridor_gen.generate_corridors(root)
        
        rooms = [leaf.room for leaf in root.get_leaf_nodes() if leaf.room]
        return root, rooms, corridors

    def test_pipeline_executes_without_errors(self):
        """1. Проверка, что вся цепочка запускается и не падает."""
        root, rooms, corridors = self._generate_full_dungeon(depth=4)
        assert len(rooms) > 0
        assert len(corridors) > 0

    def test_rooms_stay_within_bsp_leaves(self):
        """2. Каждая комната должна целиком лежать внутри своего BSP-листа."""
        root, rooms, _ = self._generate_full_dungeon(depth=4)
        leaves = root.get_leaf_nodes()
        
        for leaf in leaves:
            if leaf.room is None:
                continue
            rx, ry, rw, rh = leaf.room
            # Комната не должна вылезать за границы листа
            assert rx >= leaf.x
            assert ry >= leaf.y
            assert rx + rw <= leaf.x + leaf.width
            assert ry + rh <= leaf.y + leaf.height

    def test_all_coordinates_within_screen_bounds(self):
        """3. Никакие точки комнат и коридоров не должны выходить за пределы экрана."""
        _, rooms, corridors = self._generate_full_dungeon(depth=4)
        
        # Проверка комнат
        for rx, ry, rw, rh in rooms:
            assert 0 <= rx and rx + rw <= SCREEN_WIDTH
            assert 0 <= ry and ry + rh <= SCREEN_HEIGHT
            
        # Проверка коридоров
        for x1, y1, x2, y2 in corridors:
            assert 0 <= x1 <= SCREEN_WIDTH and 0 <= x2 <= SCREEN_WIDTH
            assert 0 <= y1 <= SCREEN_HEIGHT and 0 <= y2 <= SCREEN_HEIGHT

    def test_corridors_connect_all_rooms(self):
        """4. Все комнаты должны быть связаны в единый граф (BFS-проверка связности)."""
        _, rooms, corridors = self._generate_full_dungeon(depth=4)
        if len(rooms) <= 1:
            pytest.skip("Нужно минимум 2 комнаты для проверки связности")

        # 1. Центры комнат
        room_centers = [(r[0] + r[2]//2, r[1] + r[3]//2) for r in rooms]
        
        # 2. Постройка графа: ребро между двумя комнатами, если коридор соединяет их центры
        #    Используем пространственную близость (< 10px погрешность)
        adj = {i: set() for i in range(len(room_centers))}
        for x1, y1, x2, y2 in corridors:
            i1 = min(range(len(room_centers)), key=lambda i: (room_centers[i][0]-x1)**2 + (room_centers[i][1]-y1)**2)
            i2 = min(range(len(room_centers)), key=lambda i: (room_centers[i][0]-x2)**2 + (room_centers[i][1]-y2)**2)
            if i1 != i2:
                adj[i1].add(i2)
                adj[i2].add(i1)

        # 3. BFS от первой комнаты
        visited = set()
        queue = deque([0])
        visited.add(0)
        while queue:
            curr = queue.popleft()
            for neighbor in adj[curr]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        # 4. Проверяем, что посетили все комнаты
        assert len(visited) == len(room_centers), (
            f"Граф не связный, Посещено {len(visited)} из {len(room_centers)} комнат. "
            f"Изолированные: {set(range(len(room_centers))) - visited}"
        )