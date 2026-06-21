"""Компонент для отображения временных уведомлений."""
import pygame
import config.display_config as display


class Notification:
    """Отрисовывает сообщение по центру экрана (например, 'Инвентарь полон')."""

    def __init__(self):
        self.font = pygame.font.Font(None, 28)

    def draw(self, surface: pygame.Surface, message: str) -> None:
        if not message:
            return

        text = self.font.render(message, True, (255, 100, 100))
        rect = text.get_rect(
            center=(display.SCREEN_WIDTH // 2, display.SCREEN_HEIGHT // 2 - 100)
        )
        
        # Небольшая подложка для читаемости
        bg_rect = rect.inflate(20, 10)
        pygame.draw.rect(surface, (0, 0, 0), bg_rect)
        
        surface.blit(text, rect)