import pytest
from generation.bsp_tree import BSPNode
from generation.room_generator import RoomGenerator

class TestRoomGenerator:
    def test_create_rooms_in_tree(self, bsp_root):
        # Разбиение дерева
        bsp_root.recursive_split(depth=3)
        gen = RoomGenerator(min_fill_ratio=0.4)
        gen.create_rooms_in_tree(bsp_root)

        leaves = bsp_root.get_leaf_nodes()
        for leaf in leaves:
            assert leaf.room is not None
            rx, ry, rw, rh = leaf.room
            # Комната должна целиком лежать внутри узла
            assert rx >= leaf.x
            assert ry >= leaf.y
            assert rx + rw <= leaf.x + leaf.width
            assert ry + rh <= leaf.y + leaf.height

    def test_get_room_closest_to(self, prepared_bsp_tree):
        gen = RoomGenerator()
        # Поиск комнаты ближе к точке (500, 50), она должна попасть в правый лист
        closest = gen.get_room_closest_to(prepared_bsp_tree, 500, 50)
        assert closest == (410, 10, 50, 50)

    def test_get_random_room_returns_valid(self, prepared_bsp_tree):
        gen = RoomGenerator()
        room = gen.get_random_room(prepared_bsp_tree)
        assert room is not None
        assert isinstance(room, tuple) and len(room) == 4