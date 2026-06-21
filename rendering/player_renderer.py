"""Рендерер для игрока - отвечает только за отрисовку (View)."""
import pygame
from config.display_config import PLAYER_COLOR


class PlayerRenderer:
    """Отвечает за визуальное представление игрока."""
    
    def __init__(self):
        """Инициализация рендерера."""
        self.color = PLAYER_COLOR
    
    def draw(self, surface: pygame.Surface, player) -> None:
        """
        Отрисовка игрока.
        
        Args:
            surface: Поверхность для отрисовки
            player: Экземпляр Player для отрисовки
        """
        pygame.draw.rect(surface, self.color, player.rect)