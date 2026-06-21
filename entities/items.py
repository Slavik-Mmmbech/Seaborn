"""
Модуль для работы с предметами в игровом мире.
Содержит классы Rarity
"""

import pygame
import config.display_config as display

from config.enums import Rarity


class Item:
    """Модуль предмета."""

    def __init__(
        self,
        name: str,
        rarity: Rarity,
        weight: float,
        value: float,
        description: str = "",
    ):
        self.name = name
        self.rarity = rarity
        self.weight = weight
        self.value = value
        self.description = description

    def __repr__(self):
        return f"{self.name}/ {self.rarity.name} / {round(self.weight, 2)} / {round(self.value, 2)}"


class Collectible:
    """Модуль сборного предмета."""

    def __init__(self, x: int, y: int, item: Item):
        """
        Создание предмета в мире.

        Attributes:
            x: позиция X.
            y: позиция Y.
            item: экземпляр класса Item.
        """
        self.rect = pygame.Rect(x, y, display.TILE_SIZE, display.TILE_SIZE)

        self.item = item

        self.image = None
        self.is_collected = False

    def try_collect(self, player_rect: pygame.Rect) -> bool:
        """
        Попытка сбора: проверяет коллизию и возвращает результат.

        Attributes:
            player_rect: Игрок

        Returns:
            True, если предмет успешно собран
        """
        return self.rect.colliderect(player_rect)
