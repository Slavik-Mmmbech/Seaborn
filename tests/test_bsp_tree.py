import pytest
from generation.bsp_tree import BSPNode

class TestBSPNode:
    def test_initial_state(self, bsp_root):
        assert bsp_root.x == 0 and bsp_root.y == 0
        assert bsp_root.width == 800 and bsp_root.height == 600
        assert bsp_root.left is None and bsp_root.right is None

    def test_split_creates_valid_children(self, bsp_root):
        success = bsp_root.split()
        if success:
            assert bsp_root.left is not None
            assert bsp_root.right is not None
            # Проверка того, что дети не авходят за границу родителя
            assert bsp_root.left.x >= bsp_root.x
            assert bsp_root.right.y >= bsp_root.y\
            
    def test_recursive_split_bounded(self, bsp_root):
        bsp_root.recursive_split(depth=4)
        leaves = bsp_root.get_leaf_nodes()
        
        assert len(leaves) > 1
        for leaf in leaves:
            # Лист не должен иметь детей
            assert leaf.left is None and leaf.right is None
            # Комната должна помещаться в область листа
            assert leaf.x >= 0 and leaf.y >= 0
            assert leaf.x + leaf.width <= 800
            assert leaf.y + leaf.height <= 600

    def test_get_center(self, bsp_root):
        cx, cy = bsp_root.get_center()
        assert cx == 400
        assert cy == 300