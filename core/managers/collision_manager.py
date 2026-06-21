import pygame
from typing import List
import config.gameplay_config as gameplay

class CollisionManager:
    """Управление коллизиями и валидацией позиций."""
    
    def __init__(self, walkable_areas: List[pygame.Rect]):
        self.walkable_areas = walkable_areas
    
    def is_position_valid(self, rect: pygame.Rect) -> bool:
        """Проверяет, находится ли центр объекта в проходимой зоне."""
        if not self.walkable_areas:
            return False
            
        center_x = rect.centerx
        center_y = rect.centery
        
        point_rect = pygame.Rect(
            center_x - gameplay.VALID_DELTA,
            center_y - gameplay.VALID_DELTA,
            gameplay.VALID_SIZE,
            gameplay.VALID_SIZE
        )
        
        return any(
            area.collidepoint(point_rect.center) 
            for area in self.walkable_areas
        )
    
    def check_collision_with_areas(self, rect: pygame.Rect) -> bool:
        """Проверяет коллизию с любой проходимой зоной."""
        return any(area.colliderect(rect) for area in self.walkable_areas)