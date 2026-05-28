"""
weighted_binary_loot.py
Генератор лута на основе взвешенного случайного выбора с бинарным поиском.
Сложность: подготовка O(n), выборка O(log n), память O(n).
"""
from __future__ import annotations

import bisect
import random
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class LootDropStrategy(ABC):
    """Интерфейс стратегии генерации дропа"""
    @abstractmethod
    def draw(self) -> Any:
        """Возвращает сгенерированный предмет."""
        raise NotImplementedError


class WeightedBinaryLootGenerator(LootDropStrategy):
    """
    Генератор лута: Weighted Random + Binary Search.
    """
    def __init__(self, loot_table: Dict[Any, float]):
        self._items: List[Any] = []
        self._cum_weights: List[float] = []
        self._total_weight: float = 0.0
        self._rebuild(loot_table)

    def _rebuild(self, loot_table: Dict[Any, float]) -> None:
        """Пересчитывает кумулятивные массивы. Вызывается при init/update."""
        self._items.clear()
        self._cum_weights.clear()
        current_sum = 0.0

        for item, weight in loot_table.items():
            if weight <= 0.0:
                continue 
            self._items.append(item)
            current_sum += weight
            self._cum_weights.append(current_sum)

        self._total_weight = current_sum
        if self._total_weight <= 0.0:
            raise ValueError("Loot table contains no valid positive weights.")

    def draw(self) -> Any:
        """
        Выбирает случайный предмет с вероятностью, пропорциональной весу.
        Использует бинарный поиск в массиве кумулятивных сумм.
        """
        if not self._items:
            raise RuntimeError("Cannot draw from an empty loot generator.")

        roll = random.uniform(0.0, self._total_weight)
        index = bisect.bisect_left(self._cum_weights, roll)
        return self._items[index]

    def update_table(self, new_loot_table: Dict[Any, float]) -> None:
        """Позволяет менять веса динамически (биом, глубина, модификаторы)."""
        self._rebuild(new_loot_table)

    @property
    def total_weight(self) -> float:
        return self._total_weight