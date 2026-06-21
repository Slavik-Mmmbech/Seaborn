"""Рендерер для предметов - отвечает за отрисовку (View)."""

import pygame
from typing import Dict

from config.enums import Rarity
from config.display_config import (
    RARITY_COLORS, BASE_COLOR, TILE_SIZE, FRAME_WIDTH
    )
from config.gameplay_config import (
    COLLECT_RECT_SIZE, COLLECT_RECT_BORDER_RADIUS
    )
from entities.items import Collectible


class CollectibleRenderer:
    """Отвечает за создание и отрисовку предметов."""

    # Кэш изображений разных редкостей для оптимизации отрисовки
    _texture_cache: Dict[Rarity, pygame.Surface] = {}

    @classmethod
    def get_texture(cls, rarity: Rarity) -> pygame.Surface:
        """Получает или создает текстуру для редкости."""
        if rarity not in cls._texture_cache:
            surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)

            base_color = RARITY_COLORS.get(rarity, BASE_COLOR)

            # Основной прямоугольник
            pygame.draw.rect(
                surface,
                base_color,
                COLLECT_RECT_SIZE,
                border_radius=COLLECT_RECT_BORDER_RADIUS,
            )
            # Рамка
            pygame.draw.rect(
                surface,
                BASE_COLOR,
                COLLECT_RECT_SIZE,
                width=FRAME_WIDTH,
                border_radius=COLLECT_RECT_BORDER_RADIUS,
            )

            cls._texture_cache[rarity] = surface

        return cls._texture_cache[rarity]

    def draw(self, screen: pygame.Surface, collectible: Collectible) -> None:
        """Отрисовка предмета на экране."""
        if collectible.is_collected:
            return

        texture = self.get_texture(collectible.item.rarity)

        screen.blit(texture, collectible.rect)
