"""Компонент полосы здоровья/кислорода."""
import pygame
import config.display_config as display
import config.gameplay_config as gameplay


class OxygenBar:
    """Отрисовывает визуальную шкалу кислорода."""

    def __init__(self, width: int = 200, height: int = 20):
        self.width = width
        self.height = height
        self.rect = pygame.Rect(10, 10, width, height)
        self.font = pygame.font.Font(None, 20)

    def draw(self, surface: pygame.Surface, current_oxygen: float) -> None:
        # Фон полосы
        pygame.draw.rect(surface, (50, 50, 50), self.rect)
        
        # Заполнение
        ratio = max(0, min(1, current_oxygen / gameplay.PLAYER_MAX_OXYGEN))
        fill_width = int(self.width * ratio)
        
        # Цвет меняется от зеленого к красному при низком кислороде
        if ratio > 0.3:
            color = (100, 200, 100)
        else:
            color = (255, 50, 50)
            
        pygame.draw.rect(surface, color, (self.rect.x, self.rect.y, fill_width, self.height))
        
        # Текст поверх
        text = self.font.render(f"O2: {int(current_oxygen)}", True, (255, 255, 255))
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)