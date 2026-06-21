"""Рендерер для игрового мира - отрисовка статических элементов."""
import pygame
from typing import List
from config.display_config import (
    WATER_COLOR,
    FLOOR_COLOR,
    WALL_COLOR,
    EXIT_COLOR
)


class WorldRenderer:
    """Отвечает за отрисовку статических элементов мира."""
    
    def __init__(self):
        """Инициализация рендерера."""
        self.water_color = WATER_COLOR
        self.floor_color = FLOOR_COLOR
        self.wall_color = WALL_COLOR
        self.exit_color = EXIT_COLOR
    
    def draw_world(self, screen: pygame.Surface, world) -> None:
        """
        Отрисовка всего мира.
        
        Args:
            screen: Экран для отрисовки
            world: Экземпляр World
        """
        # 1. Фон (вода)
        screen.fill(self.water_color)
        
        # 2. Проходимые зоны (пол)
        self._draw_walkable_areas(screen, world.walkable_areas)
        
        # 3. Границы комнат (стены)
        self._draw_room_borders(screen, world.rooms)
        
        # 4. Зона выхода
        if world.exit_rect:
            self._draw_exit_zone(screen, world.exit_rect)
    
    def _draw_walkable_areas(self, screen: pygame.Surface, areas: List[pygame.Rect]) -> None:
        """Отрисовка проходимых зон."""
        for area in areas:
            pygame.draw.rect(screen, self.floor_color, area)
    
    def _draw_room_borders(self, screen: pygame.Surface, rooms: List[pygame.Rect]) -> None:
        """Отрисовка границ комнат."""
        for room in rooms:
            pygame.draw.rect(screen, self.wall_color, room, width=1)
    
    def _draw_exit_zone(self, screen: pygame.Surface, exit_rect: pygame.Rect) -> None:
        """Отрисовка зоны выхода."""
        pygame.draw.rect(screen, self.exit_color, exit_rect, width=2)
    
    def draw_debug(self, screen: pygame.Surface, world) -> None:
        """
        Отладочная отрисовка.
        
        Args:
            screen: Экран для отрисовки
            world: Экземпляр World
        """
        # Полупрозрачный слой для walkable areas
        debug_surface = pygame.Surface(screen.get_size())
        debug_surface.set_alpha(50)
        debug_surface.fill((0, 255, 0))
        
        for area in world.walkable_areas:
            pygame.draw.rect(debug_surface, (0, 255, 0), area)
        
        screen.blit(debug_surface, (0, 0))
        
        # Нумерация комнат
        font = pygame.font.Font(None, 24)
        for i, room in enumerate(world.rooms):
            color = (100 + (i * 30) % 100, 150 + (i * 20) % 50, 100)
            pygame.draw.rect(screen, color, room)
            pygame.draw.rect(screen, (255, 255, 255), room, width=1)
            
            text = font.render(str(i), True, (255, 255, 255))
            screen.blit(text, (room.centerx - 10, room.centery - 10))
        
        # Коридоры
        for corridor in world.corridors:
            x1, y1, x2, y2 = corridor
            pygame.draw.line(screen, (255, 200, 0), (x1, y1), (x2, y2), width=4)
            pygame.draw.circle(screen, (255, 100, 0), (x1, y1), 3)
            pygame.draw.circle(screen, (255, 100, 0), (x2, y2), 3)