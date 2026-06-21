import pytest

from config.generation_config import MAX_DEPTH
from spatial.quadtree import Bounds, QuadTree

class TestBounds:
    """Тесты геометрических операций над прямоугольными областями."""
    
    def test_contains_true(self):
        outer = Bounds(0, 0, 100, 100)
        inner = Bounds(10, 10, 20, 20)
        assert outer.contains(inner)

    def test_contains_false_edge_overlap(self):
        outer = Bounds(0, 0, 10, 10)
        inner = Bounds(5, 5, 6, 6)
        assert not outer.contains(inner)

    def test_intersects_true(self):
        a = Bounds(0, 0, 10, 10)
        b = Bounds(5, 5, 10, 10)
        assert a.intersects(b)

    def test_intersects_false(self):
        a = Bounds(0, 0, 5, 5)
        b = Bounds(6, 6, 5, 5)
        assert not a.intersects(b)


class TestQuadTree:
    """Тесты структуры QuadTree и её методов."""
    
    @pytest.fixture
    def tree(self) -> QuadTree:
        return QuadTree(Bounds(0, 0, 100, 100))

    def test_insert_and_query_single(self, tree):
        item, b = "Entity_A", Bounds(10, 10, 5, 5)
        assert tree.insert(item, b)
        assert tree.query(b) == [item]

    def test_insert_out_of_bounds(self, tree):
        # Попытка вставить объект вне границ корня
        assert not tree.insert("Out", Bounds(105, 105, 10, 10))
        assert len(tree.query(Bounds(0, 0, 100, 100))) == 0

    def test_subdivision_on_capacity(self, tree):
        # MAX_CAPACITY = 4. После 5-й вставки должно произойти разбиение
        for i in range(5):
            tree.insert(f"Obj_{i}", Bounds(i*10, i*10, 5, 5))
        assert tree.children[0] is not None, "Узел должен был разделиться"

    def test_query_multiple_intersections(self, tree):
        tree.insert("A", Bounds(10, 10, 10, 10))
        tree.insert("B", Bounds(20, 20, 10, 10))
        results = tree.query(Bounds(15, 15, 20, 20))
        assert set(results) == {"A", "B"}

    def test_query_empty_result(self, tree):
        tree.insert("A", Bounds(0, 0, 5, 5))
        assert tree.query(Bounds(50, 50, 10, 10)) == []

    def test_clear_resets_structure(self, tree):
        for _ in range(5):
            tree.insert("X", Bounds(10, 10, 5, 5))
        tree.clear()
        assert len(tree.items) == 0
        assert all(child is None for child in tree.children)

    def test_max_depth_limits_recursion(self):
        tree = QuadTree(Bounds(0, 0, 100, 100))
        # Вставка 100 мелких объектов должна остановиться на depth=5
        for i in range(100):
            tree.insert(f"Deep_{i}", Bounds(i % 90, (i // 90) * 10, 2, 2))
        
        def count_depth(node: QuadTree, current=0):
            if node.children[0] is None:
                return current
            return max(count_depth(c, current + 1) for c in node.children)
            
        assert count_depth(tree) <= MAX_DEPTH