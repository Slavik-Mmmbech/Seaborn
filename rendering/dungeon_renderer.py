# rendering/dungeon_renderer.py
import pygame
from typing import List, Tuple
import config.display_config as display

class DungeonRenderer:
    """
    Отрисовка геометрии подземелья (View).
    Преобразует чистые данные (tuple) в pygame.Rect для отрисовки.
    """
    
    def __init__(self):
        self.corridor_width = display.CORRIDOR_WIDTH
        self.wall_thickness = display.WALL_THICKNESS
    
    def draw_rooms(
        self, 
        screen: pygame.Surface, 
        rooms: List[Tuple[int, int, int, int]],
        show_numbers: bool = False
    ) -> None:
        """
        Отрисовывает комнаты.
        
        Args:
            screen: Поверхность для отрисовки
            rooms: Список комнат (x, y, width, height)
            show_numbers: Показывать номера комнат
        """
        for i, room_data in enumerate(rooms):
            room_rect = pygame.Rect(*room_data)
            
            color = self._get_room_color(i)
            pygame.draw.rect(screen, color, room_rect)
            pygame.draw.rect(screen, display.BASE_COLOR, room_rect, width=1)
            
            if show_numbers:
                self._draw_room_number(screen, room_rect, i)
    
    def draw_corridors(
        self, 
        screen: pygame.Surface, 
        corridors: List[Tuple[int, int, int, int]]
    ) -> None:
        """
        Отрисовывает коридоры как линии.
        
        Args:
            screen: Поверхность для отрисовки
            corridors: Список коридоров (x1, y1, x2, y2)
        """
        for corridor in corridors:
            x1, y1, x2, y2 = corridor
            
            # Основная линия коридора
            pygame.draw.line(
                screen, 
                display.CORRIDOR_COLOR,
                (x1, y1), 
                (x2, y2), 
                width=self.corridor_width
            )
    
    def draw_walkable_areas(
        self, 
        screen: pygame.Surface, 
        rooms: List[Tuple[int, int, int, int]],
        corridors: List[Tuple[int, int, int, int]],
        alpha: int = 50
    ) -> None:
        """
        Отрисовывает все проходимые зоны (комнаты + коридоры).
        """
        debug_surface = pygame.Surface(
            (display.SCREEN_WIDTH, display.SCREEN_HEIGHT), 
            pygame.SRCALPHA
        )
        
        # Комнаты
        for room_data in rooms:
            room_rect = pygame.Rect(*room_data)
            pygame.draw.rect(debug_surface, (0, 255, 0, alpha), room_rect)
        
        # Коридоры
        half_width = self.corridor_width // 2
        for corridor in corridors:
            x1, y1, x2, y2 = corridor
            
            if x1 == x2:  # Вертикальный
                corridor_rect = pygame.Rect(
                    x1 - half_width, 
                    min(y1, y2),
                    self.corridor_width, 
                    abs(y2 - y1)
                )
            else:  # Горизонтальный
                corridor_rect = pygame.Rect(
                    min(x1, x2), 
                    y1 - half_width,
                    abs(x2 - x1), 
                    self.corridor_width
                )
            
            pygame.draw.rect(debug_surface, (0, 255, 0, alpha), corridor_rect)
        
        screen.blit(debug_surface, (0, 0))
    
    def draw_walls(
        self, 
        screen: pygame.Surface, 
        walls: List[pygame.Rect]
    ) -> None:
        """Отрисовывает стены."""
        for wall in walls:
            pygame.draw.rect(screen, display.WALL_COLOR, wall)
    
    def _get_room_color(self, index: int) -> Tuple[int, int, int]:
        """Генерирует цвет комнаты на основе индекса."""
        return (
            80 + (index * 25) % 100,
            130 + (index * 20) % 50,
            180
        )
    
    def _draw_room_number(
        self, 
        screen: pygame.Surface, 
        room_rect: pygame.Rect, 
        number: int
    ) -> None:
        """Рисует номер комнаты в центре."""
        font = pygame.font.Font(None, 24)
        text = font.render(str(number), True, (255, 255, 255))
        screen.blit(text, (room_rect.centerx - 10, room_rect.centery - 10))