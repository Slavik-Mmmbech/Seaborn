"""
Модуль реализации цепи Маркова для процедурной генерации.

Использует кумулятивное распределение вероятностей и бинарный поиск
для эффективного сэмплирования следующего состояния.

Сложность алгоритмов:
- Предрасчёт кумулятивных весов: O(n) для каждого состояния
- Сэмплирование следующего состояния: O(log n) через bisect
- Генерация последовательности: O(m * log n), где m - длина, n - количество состояний
"""

import random
from bisect import bisect_left
from typing import Dict, List

import config.content_config as content
from config.logging_config import setup_logger

logger = setup_logger(__name__)


class MarkovChain:
    """
    Цепь Маркова для процедурной генерации последовательностей.
    
    Использует взвешенные вероятности переходов между состояниями.
    Для эффективности предварительно вычисляет кумулятивные распределения.
    
    Attributes:
        transitions: Словарь переходов {состояние: {следующее_состояние: вес}}.
        _cum_weights: Предвычисленные кумулятивные веса для каждого состояния.
        _state_pool: Списки возможных следующих состояний для каждого состояния.
    
    Example:
        >>> transitions = {
        ...     "A": {"B": 0.7, "C": 0.3},
        ...     "B": {"A": 0.5, "C": 0.5},
        ...     "C": {}
        ... }
        >>> chain = MarkovChain(transitions)
        >>> sequence = chain.generate(start_state="A", length=5)
    """

    def __init__(self, transitions: Dict[str, Dict[str, float]]):
        """
        Инициализация цепи Маркова.
        
        Args:
            transitions: Словарь переходов между состояниями.
                        Формат: {состояние: {следующее_состояние: вероятность}}.
        """
        self.transitions = transitions
        self._cum_weights: Dict[str, List[float]] = {}
        self._state_pool: Dict[str, List[str]] = {}
        self._precompute()

    def _precompute(self) -> None:
        """
        Предвычисление кумулятивных распределений для всех состояний.
        
        Сложность: O(S * N), где S - количество состояний,
                   N - среднее количество переходов из состояния.
        
        Создаёт два словаря:
        - _cum_weights: кумулятивные суммы вероятностей
        - _state_pool: списки возможных следующих состояний
        """
        for current_state, next_states in self.transitions.items():
            states = list(next_states.keys())
            probs = list(next_states.values())

            # Вычисление кумулятивных весов
            cum = []
            acc = content._UNIFORM_MIN
            for p in probs:
                acc += p
                cum.append(acc)

            self._cum_weights[current_state] = cum
            self._state_pool[current_state] = states

    def _sample_next(self, current: str) -> str:
        """
        Выбор следующего состояния по взвешенным вероятностям.
        
        Использует бинарный поиск (bisect_left) для эффективного
        сэмплирования из кумулятивного распределения.
        
        Сложность: O(log n), где n - количество возможных переходов.
        
        Args:
            current: Текущее состояние.
            
        Returns:
            Следующее состояние, выбранное согласно вероятностям.
            
        Note:
            Если у текущего состояния нет исходящих переходов (терминальное),
            выбирается случайное состояние из всех доступных (fallback).
        """
        # Проверка на терминальное состояние
        if self.transitions[current] == content._EMPTY_TRANSITIONS:
            logger.debug(f"Проблема: {current} не имеет состояний -> fallback")
            return random.choice(list(self.transitions.keys()))

        cum = self._cum_weights[current]
        pool = self._state_pool[current]

        # Генерация случайного значения и бинарный поиск
        rand_val = random.uniform(content._UNIFORM_MIN, cum[-1])
        idx = bisect_left(cum, rand_val)
        return pool[idx]

    def generate(
        self,
        start_state: str = content.LORE_CONTEXT_START,
        length: int = content.DEFAULT_GENERATION_LENGTH
        ) -> List[str]:
        """
        Генерация последовательности состояний заданной длины.
        
        Сложность: O(m * log n), где m - длина последовательности,
                   n - среднее количество переходов из состояния.
        
        Args:
            start_state: Начальное состояние цепи.
            length: Требуемая длина последовательности.
            
        Returns:
            Список состояний, начиная с start_state.
            
        Raises:
            ValueError: Если length <= 0 (возвращается пустой список).
            
        Example:
            >>> chain.generate(start_state="A", length=5)
            ['A', 'B', 'C', 'A', 'B']
        """
        if length <= 0:
            return []

        sequence = [start_state]
        current = start_state
        for _ in range(content._SEQUENCE_START_INDEX, length):
            current = self._sample_next(current)
            sequence.append(current)
        return sequence
