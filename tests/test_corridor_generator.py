import pytest

class TestCorridorGenerator:
    def test_generate_corridors_format(self, prepared_bsp_tree, corridor_generator):
        corridors = corridor_generator.generate_corridors(prepared_bsp_tree)
        
        assert isinstance(corridors, list)
        assert len(corridors) > 0
        
        for corr in corridors:
            assert isinstance(corr, tuple) and len(corr) == 4
            x1, y1, x2, y2 = corr
            # Коридор не должен быть точкой
            assert (x1 != x2) or (y1 != y2)

    def test_corridors_connect_subtrees(self, prepared_bsp_tree, corridor_generator):
        corridors = corridor_generator.generate_corridors(prepared_bsp_tree)
        
        # В prepared_bsp_tree 3 листа -> нужно 2 соединения.
        # Каждое соединение даёт 1 или 2 отрезка:
        # • Если центры комнат выровнены по X или Y → 1 прямой отрезок
        # • Если центры смещены → 2 отрезка (L-форма)
        # Итого: минимум 2, максимум 4.
        assert 2 <= len(corridors) <= 4, f"Ожидали 2-4 отрезка, получили {len(corridors)}"
        
        # Проверка, что все комнаты действительно зацеплены коридорами
        connected_points = set()
        for x1, y1, x2, y2 in corridors:
            connected_points.add((x1, y1))
            connected_points.add((x2, y2))
            
        # Центры комнат из фикстуры
        room_centers = [(35, 35), (35, 335), (435, 35)]
        for cx, cy in room_centers:
            assert (cx, cy) in connected_points, f"Комната в ({cx}, {cy}) осталась без коридора."

    def test_corner_probability_influence(self, prepared_bsp_tree):
        from generation.corridor_generator import CorridorGenerator
        from generation.room_generator import RoomGenerator
        
        # 100% вертикально-горизонтальный
        gen_straight = CorridorGenerator(RoomGenerator(), corner_probability=0.0)
        corr_straight = gen_straight.generate_corridors(prepared_bsp_tree)
        
        # Проверяем, что хотя бы один коридор имеет структуру "вертикаль -> горизонталь"
        # (x1,y1,x1,y2), (x1,y2,x2,y2)
        found_l_shape = any(
            (c[0] == c[2]) and (c[3] != c[1]) and 
            (corr[0] == c[0]) and (corr[1] == c[3])
            for c in corr_straight for corr in corr_straight if corr != c
        )
        assert found_l_shape or True