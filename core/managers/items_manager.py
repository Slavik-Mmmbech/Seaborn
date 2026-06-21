import random
from typing import List, Tuple, Any
import pygame
from entities.items import Item
from entities.items import Collectible
from loot.loot_bag import LootBag
import config.gameplay_config as gameplay
import config.generation_config as gen

class CollectibleSpawnManager:
    """Управление генерацией и случайным спавном предметов (Collectible) в комнатах."""
    
    def __init__(self, rooms: List[Tuple[int, int, int, int]], room_values: dict):
        """
        :param rooms: Список комнат в формате (x, y, width, height).
        :param room_values: Словарь весов комнат {index: weight} для алгоритма распределения.
        """
        self.rooms = rooms
        self.room_values = room_values
        
    def spawn_collectibles(self, count: Any = None) -> List[Collectible]:
        """Спавнит предметы в комнатах с учетом весовых коэффициентов ценности комнат."""
        if count is None:
            count = gameplay.COLLECTIBLES_COUNT
            
        if not self.rooms:
            return []
            
        bag = LootBag()
        collectibles = []
        
        room_weights = self._calculate_room_weights()
        
        for _ in range(count):
            collectible = self._create_single_collectible(bag, room_weights)
            collectibles.append(collectible)
            
        return collectibles
    
    def _calculate_room_weights(self) -> List[float]:
        """Рассчитывает веса комнат. Если все веса равны нулю, распределяет равномерно."""
        weights = [
            self.room_values.get(i, 0.0) 
            for i in range(len(self.rooms))
        ]
        
        if sum(weights) == 0:
            weights = [1.0] * len(self.rooms)
            
        return weights
    
    def _create_single_collectible(self, bag: LootBag, room_weights: List[float]) -> Collectible:
        """Создает единичный экземпляр Collectible, выбирая случайную редкость и комнату."""
        rarity = bag.draw()
        rarity_cfg = gameplay.ITEM_RARITY_CONFIG[rarity]
        min_w, max_w, value_mult, _ = rarity_cfg
        
        item = Item(
            "loot",
            rarity,
            random.uniform(min_w, max_w),
            random.uniform(gameplay.LOW_VALUE, gameplay.HIGH_VALUE) * value_mult,
        )
        
        room_data = random.choices(self.rooms, weights=room_weights)[0]
        room = pygame.Rect(*room_data)
        
        spawn_x, spawn_y = self._calculate_spawn_position(room)
        
        return Collectible(spawn_x, spawn_y, item)
    
    def _calculate_spawn_position(self, room: pygame.Rect) -> Tuple[int, int]:
        """Вычисляет безопасные координаты спавна внутри Rect с учетом технологических отступов."""
        padding = gen.ROOM_OFFSET
        min_x, max_x = room.left + padding, room.right - padding
        min_y, max_y = room.top + padding, room.bottom - padding
        
        safe_x = min_x if max_x <= min_x else random.randint(min_x, max_x)
        safe_y = min_y if max_y <= min_y else random.randint(min_y, max_y)
        
        return (safe_x, safe_y)