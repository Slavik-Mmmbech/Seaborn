"""Базовый интерфейс для всех экранов игры."""
from abc import ABC, abstractmethod
from typing import Any
import pygame


class BaseScreen(ABC):
    """Абстрактный экран. Реализует паттерн Strategy для Game."""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> str | None:
        """
        Обрабатывает событие.
        Возвращает строку-команду ('next_screen', 'quit', 'resume') или None.
        """
        pass

    @abstractmethod
    def draw(self) -> None:
        """Отрисовывает экран."""
        pass

    def update(self, delta_time: float) -> None:
        """Опциональное обновление состояния (для анимаций и т.д.)."""
        pass