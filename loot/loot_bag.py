"""
Модуль реализации генератора последовательности редкостей по принципу Shuffle Bag.
Обеспечивает контролируемое случайное распределение предметов, предотвращая 
длинные серии одинаковых дропов (как в чистом рандоме).

Компоненты:
    LootBag: класс-генератор, управляющий мешком с редкостями.

Алгоритмы:
    - Shuffle Bag: O(n) для пересоздания мешка, O(1) для извлечения предмета.
    - Fisher-Yates shuffle: O(n) для перемешивания массива.
"""
import random

from config.gameplay_config import ITEM_RARITY_CONFIG, SHUFFLE_BAG_SIZE
from config.generation_config import LAST_RARITY_INDEX
from entities.items import Rarity

class LootBag:
    """
    Класс-генератор редкостей на основе паттерна Shuffle Bag.
    Формирует пул предметов на основе весов, перемешивает его 
    и отдаёт предметы по одному. При исчерпании пула — автоматически перегенерирует.

    Attributes:
        _bag: Внутренний список (мешок) с текущими доступными редкостями.
    """
    
    def __init__(self):
        """
        Инициализирует генератор и сразу заполняет мешок первой партией предметов.
        """
        #Внутреннее состояние мешка
        self._bag: list[Rarity] = []
        self._refill()

    def _refill(self) -> None:
        """
        Формирует новый мешок на основе весов из конфигурации и перемешивает его.
        
        Использует алгоритм Fisher-Yates (через random.shuffle) для честного 
        перемешивания. Последний элемент в отсортированном списке забирает 
        все оставшиеся слоты, чтобы сумма предметов точно равнялась SHUFFLE_BAG_SIZE.

        Raises:
            ValueError: Если SHUFFLE_BAG_SIZE <= 0 (защита от невалидной конфигурации).
        """
        if SHUFFLE_BAG_SIZE <= 0:
            raise ValueError("SHUFFLE_BAG_SIZE must be greater than zero.")
        
        self._bag.clear()
        remaining_slots = SHUFFLE_BAG_SIZE

        # Сортировка редкостей по весу (индекс 3 в кортеже конфигурации) по убыванию
        rarity_sorted = sorted(
            ITEM_RARITY_CONFIG.items(), 
            key=lambda x: x[1][3], 
            reverse=True
        )
        
        for i, (rarity, cfg) in enumerate(rarity_sorted):
            if i == len(rarity_sorted) + LAST_RARITY_INDEX:
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
        
        Сложность: O(1) для извлечения (pop), O(n) если требуется перегенерация мешка.

        Returns:
            Rarity: Случайная редкость из текущего распределения.
        """
        if not self._bag:
            self._refill()
        return self._bag.pop()
