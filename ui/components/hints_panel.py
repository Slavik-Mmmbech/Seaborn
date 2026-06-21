"""Компонент панели подсказок управления."""
import pygame


class HintsPanel:
    """Отрисовывает список клавиш управления в углу экрана."""

    def __init__(self):
        self.font = pygame.font.Font(None, 20)
        self.hints = [
            "WASD - Движение",
            "E - Диалог",
            "R - Рестарт/Выход",
            "ESC - Пауза",
        ]

    def draw(self, surface: pygame.Surface, x: int, y: int) -> None:
        for i, hint in enumerate(self.hints):
            text = self.font.render(hint, True, (200, 200, 200))
            surface.blit(text, (x, y + i * 20))