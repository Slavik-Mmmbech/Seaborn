# generation/loot_bag.py
"""
Модуль: генератор последовательности редкостей по принципу Shuffle Bag.
Обеспечивает контролируемое случайное распределение предметов.
"""
import random
from typing import Generator
from config import ITEM_RARITY_CONFIG, SHUFFLE_BAG_SIZE
from entities.item import Rarity

class LootBag:
    """
    Класс-генератор редкостей.
    Работает как колода карт: формирует набор, перемешивает, отдаёт по одному.
    При исчерпании — перегенерирует.
    """
    
    def __init__(self):
        # 🔹 Внутреннее состояние: список редкостей в текущем "мешке"
        self._bag: list[Rarity] = []
        # 🔹 Заполняем при инициализации
        self._refill()

    def _refill(self) -> None:
        """Формирует новый мешок на основе весов из config.py и перемешивает."""
        self._bag.clear()
        
        # 🔹 Преобразуем вероятности в целочисленные квоты
        # Пример: COMMON=0.70, BAG_SIZE=100 → 70 слотов
        remaining_slots = SHUFFLE_BAG_SIZE
        rarity_sorted = sorted(
            ITEM_RARITY_CONFIG.items(), 
            key=lambda x: x[1][3], 
            reverse=True
        )
        
        for i, (rarity, cfg) in enumerate(rarity_sorted):
            if i == len(rarity_sorted) - 1:
                # Последней редкости отдаём всё, что осталось (избегаем ошибок округления)
                count = remaining_slots
            else:
                count = round(cfg[3] * SHUFFLE_BAG_SIZE)
                count = min(count, remaining_slots)  # Защита от переполнения
                
            self._bag.extend([rarity] * count)
            remaining_slots -= count
            
        # 🔹 Перемешивание (алгоритм Fisher-Yates под капотом в Python)
        random.shuffle(self._bag)

    def draw(self) -> Rarity:
        """
        Возвращает следующую редкость из мешка.
        При пустом мешке автоматически перегенерирует.
        """
        if not self._bag:
            self._refill()
        return self._bag.pop()

    def __iter__(self) -> Generator[Rarity, None, None]:
        """Позволяет использовать LootBag в цикле или с next()."""
        return self