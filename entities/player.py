"""Модуль игрока и инвентаря."""

import pygame
from config.gameplay_config import (
    PLAYER_MAX_OXYGEN,
    PLAYER_MOVE_SPEED,
    INVENTORY_MAX_WEIGHT,
    PLAYER_HEIGHT,
    PLAYER_WIDTH,
    SPEED_PENALTY_FACTOR,
)
from entities.items import Item
from typing import List

class Inventory:
    """Управление инвентарем игрока."""
    
    def __init__(self, max_weight: float):
        self.items: List[Item] = []
        self.max_weight = max_weight
        self.current_weight = 0.0
    
    def can_add(self, item: Item) -> bool:
        """Проверяет возможность добавления предмета."""
        return self.current_weight + item.weight <= self.max_weight
    
    def add(self, item: Item) -> bool:
        """Добавляет предмет в инвентарь."""
        if not self.can_add(item):
            return False
        
        self.items.append(item)
        self.current_weight += item.weight
        return True
    
    def get_total_value(self) -> float:
        """Вычисляет общую ценность предметов."""
        if len(self.items) < 1:
            return 0.0
        return sum(item.value for item in self.items)
    
    def get_weight_penalty(self) -> float:
        """Возвращает штраф скорости от веса (0.0-1.0)."""
        return self.current_weight / self.max_weight
    
    def __len__(self) -> int:
        return len(self.items)

    def __iter__(self):
        return iter(self.items)

    def __bool__(self) -> bool:
        return len(self.items) > 0
    def __getitem__(self, index):
        """Поддержка индексации и срезов"""
        return self.items[index]

class Player:
    """Модуль игрока."""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.base_speed = PLAYER_MOVE_SPEED
        self.speed = PLAYER_MOVE_SPEED
        self.oxygen = float(PLAYER_MAX_OXYGEN)
        self.rect = pygame.Rect(
            int(x - self.width // 2), int(y - self.height // 2),
            self.width,
            self.height
        )
        self.full_collection = []
        self.inventory = Inventory(INVENTORY_MAX_WEIGHT)
        self.entry_position = None

    def pickup(self, item: Item) -> bool:
        """Подбор предмета и пересчет скорости."""
        if not self.inventory.add(item):
            return False

        penalty = self.inventory.get_weight_penalty()
        self.speed = self.base_speed * (1 - penalty * SPEED_PENALTY_FACTOR)
        return True

    def calculate_score(self) -> float:
        """Считает общую ценность собранного."""
        return self.inventory.get_total_value()

    def handle_input(self, keys: dict) -> None:
        "Движение игрока"
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.y -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.y += self.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.x -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.x += self.speed

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
