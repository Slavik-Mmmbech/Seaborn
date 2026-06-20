# generation/loot_bag.py
"""
Генератор последовательности редкостей по принципу Shuffle Bag.
Обеспечивает контролируемое случайное распределение предметов.
"""
import random
from config.gameplay_config import ITEM_RARITY_CONFIG, SHUFFLE_BAG_SIZE
from entities.items import Rarity

class LootBag:
    """
    Класс-генератор редкостей.
    Формирует набор, перемешивает, отдаёт по одному.
    При исчерпании — перегенерирует.
    """
    
    def __init__(self):
        #Внутреннее состояние мешка
        self._bag: list[Rarity] = []
        self._refill()

    def _refill(self) -> None:
        """Формирует новый мешок на основе весов из и перемешивает."""
        self._bag.clear()
        
        remaining_slots = SHUFFLE_BAG_SIZE
        rarity_sorted = sorted(
            ITEM_RARITY_CONFIG.items(), 
            key=lambda x: x[1][3], 
            reverse=True
        )
        
        for i, (rarity, cfg) in enumerate(rarity_sorted):
            if i == len(rarity_sorted) - 1:
                count = remaining_slots
            else:
                count = round(cfg[3] * SHUFFLE_BAG_SIZE)
                count = min(count, remaining_slots)  # Проверка наличия места
                
            self._bag.extend([rarity] * count)
            remaining_slots -= count
            
        # Перемешивание (алгоритм Fisher-Yates)
        random.shuffle(self._bag)

    def draw(self) -> Rarity:
        """
        Возвращает следующую редкость из мешка.
        При пустом мешке автоматически мешок сгенерирует.
        """
        if not self._bag:
            self._refill()
        return self._bag.pop()

    # def __iter__(self) -> Generator[Rarity, None, None]:
    #     """Позволяет использовать LootBag в цикле или с next()."""
    #     return self