"""
Модуль реализации генератора лута на основе взвешенного случайного выбора 
с использованием бинарного поиска.

Компоненты:
    LootDropStrategy: Абстрактный интерфейс стратегии генерации дропа.
    WeightedBinaryLootGenerator: Конкретная реализация с бинарным поиском.

Алгоритмы:
    - Подготовка (rebuild): O(n) для расчета кумулятивных сумм.
    - Выборка (draw): O(log n) благодаря бинарному поиску (bisect).
    - Память: O(n) для хранения массивов предметов и весов.
"""
from __future__ import annotations

import bisect
import random
from abc import ABC, abstractmethod
from typing import Any, Dict, List


class LootDropStrategy(ABC):
    """
    Абстрактный интерфейс стратегии генерации дропа.
    Реализует паттерн Strategy, позволяя подменять алгоритмы генерации лута 
    без изменения клиентского кода (Принцип Open/Closed из SOLID).
    """

    @abstractmethod
    def draw(self) -> Any:
        """
        Возвращает сгенерированный предмет согласно логике стратегии.

        Returns:
            Any: Сгенерированный предмет.
            
        Raises:
            NotImplementedError: Если метод не реализован в наследнике.
        """
        raise NotImplementedError


class WeightedBinaryLootGenerator(LootDropStrategy):
    """
    Генератор лута: Weighted Random + Binary Search.
    
    Оптимизирован для частых запросов (draw). Подготовка таблицы занимает O(n), 
    но каждая последующая выборка работает за O(log n), быстрее 
    стандартного линейного поиска O(n).

    Attributes:
        _items: Список предметов, отсортированный по весам.
        _cum_weights: Список кумулятивных (накопительных) весов.
        _total_weight: Суммарный вес всех предметов в таблице.
    """
    def __init__(self, loot_table: Dict[Any, float]):
        """
        Инициализация генератора и построение кумулятивных массивов.

        Args:
            loot_table: Словарь вида {Предмет: Вес}. Веса должны быть > 0.
            
        Raises:
            ValueError: Если в таблице нет ни одного валидного положительного веса.
        """
        self._items: List[Any] = []
        self._cum_weights: List[float] = []
        self._total_weight: float = 0.0
        self._rebuild(loot_table)

    def _rebuild(self, loot_table: Dict[Any, float]) -> None:
        """
        Пересчитывает кумулятивные массивы. Вызывается при инициализации или обновлении.
        
        Отфильтровывает предметы с нулевым или отрицательным весом.

        Args:
            loot_table: Словарь с новыми весами предметов.
            
        Raises:
            ValueError: Если после фильтрации не осталось валидных весов.
        """
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
        Выбирает случайный предмет с вероятностью, пропорциональной его весу.
        Использует бинарный поиск (bisect_left) в массиве кумулятивных сумм.

        Сложность: O(log n), где n - количество предметов в таблице.

        Returns:
            Any: Выбранный предмет.
            
        Raises:
            RuntimeError: Если попытка сделать выборку из пустого генератора.
        """
        if not self._items:
            raise RuntimeError("Cannot draw from an empty loot generator.")

        # Генерируем случайное число от 0 до общего веса
        roll = random.uniform(0.0, self._total_weight)
        # Бинарный поиск позиции
        index = bisect.bisect_left(self._cum_weights, roll)
        return self._items[index]

    def update_table(self, new_loot_table: Dict[Any, float]) -> None:
        """
        Позволяет менять веса динамически.
        
        Args:
            new_loot_table: Новый словарь весов для перестроения генератора.
        """
        self._rebuild(new_loot_table)

    @property
    def total_weight(self) -> float:
        """
        Геттер для получения суммарного веса таблицы.
        
        Returns:
            float: Суммарный вес всех предметов.
        """
        return self._total_weight