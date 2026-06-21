"""Рендерер для подземелья - отвечает за отрисовку (View)."""

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
            pygame.draw.rect(screen,
                             display.BASE_COLOR,
                             room_rect,
                             width=display.FRAME_WIDTH
                             )
            
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
        alpha: int = display.ALPHA
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
        
        screen.blit(debug_surface, display.BASE_COORDS)
    
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
        red_value = (index * display.RED_DELTA) % display.RED_PERC
        green_value = (index * display.GREEN_DELTA) % display.GREEN_PREC
        return (
            display.ROOM_RED_FACTOR + red_value,
            display.ROOM_GREEN_FACTOR + green_value,
            display.ROOM_BLUE_FACTOR
        )
    
    def _draw_room_number(
        self, 
        screen: pygame.Surface, 
        room_rect: pygame.Rect, 
        number: int
    ) -> None:
        """Рисует номер комнаты в центре."""
        font = pygame.font.Font(None, 24)
        text = font.render(str(number), True, display.BASE_COLOR)
        screen.blit(text, 
                    (room_rect.centerx - display.ROOM_NUMBER_DELTA,
                     room_rect.centery - display.ROOM_NUMBER_DELTA)
                    )