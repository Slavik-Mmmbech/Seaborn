"""
Модуль: предметы в игровом мире и модель данных.
"""
from enum import Enum
import pygame
import config

class Rarity(Enum):
    """Виды редкостей предметов"""

    COMMON = 'Common'
    RARE = 'Rare'
    EPIC = 'Epic'
    LEGENDARY = 'Legendary'
    ANCIENT = 'Ancient'


class Item:
    def __init__(self, name: str, rarity: Rarity, weight: float, value: int, description: str = ""):
        self.name = name
        self.rarity = rarity
        self.weight = weight
        self.value = value 
        self.description = description


    def __repr__(self):
        return f"{self.name}/💎 {self.rarity.name} / {self.weight} / {self.value} / Описание: {self.description}"
    
class Collectible:
    RARITY_COLORS = {
        Rarity.COMMON:    (200, 200, 200),  # Серый
        Rarity.RARE:      (100, 150, 255),  # Голубой
        Rarity.EPIC:      (200, 100, 255),  # Фиолетовый
        Rarity.LEGENDARY: (255, 215, 0),    # Золотой
        Rarity.ANCIENT:  (255, 170, 0),  # Оранжевый
    }

    def __init__(self, x: int, y: int, item: Item):
        """
        Создание предмета в мире.
        :param x: позиция X (пиксели)
        :param y: позиция Y (пиксели)
        :param item: экземпляр класса Item (модель данных)
        """
        self.rect = pygame.Rect(x, y, config.TILE_SIZE, config.TILE_SIZE)
        
        self.item = item
        
        self.image = pygame.Surface((config.TILE_SIZE, config.TILE_SIZE), pygame.SRCALPHA)
        base_color = self.RARITY_COLORS.get(item.rarity, (255, 255, 255))
        pygame.draw.rect(self.image, base_color, (4, 4, 24, 24), border_radius=4)
        pygame.draw.rect(self.image, (255, 255, 255), (4, 4, 24, 24), width=1, border_radius=4)

        self.is_collected = False

    def try_collect(self, collector_rect: pygame.Rect) -> bool:
        """
        Попытка сбора: проверяет коллизию и возвращает результат.
        :param collector_rect: хитбокс игрока
        :return: True, если предмет успешно собран
        """
        if self.is_collected:
            return False  # Уже собран
        
        if self.rect.colliderect(collector_rect):
            self.is_collected = True
            return True  # Успешный сбор
        return False  # Нет коллизии

    def draw(self, surface: pygame.Surface):
        """Отрисовка, только если предмет ещё не собран."""
        if not self.is_collected:
            surface.blit(self.image, self.rect)