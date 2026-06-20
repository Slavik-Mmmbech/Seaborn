import random
from bisect import bisect_left
from typing import Dict, List

from config.content_config import DEFAULT_GENERATION_LENGTH, LORE_CONTEXT_START
from config.logging_config import setup_logger

logger = setup_logger(__name__)


class MarkovChain:
    """
    Цепь Маркова для генерации.
    """

    def __init__(self, transitions: Dict[str, Dict[str, float]]):
        self.transitions = transitions
        self._cum_weights: Dict[str, List[float]] = {}
        self._state_pool: Dict[str, List[str]] = {}
        self._precompute()

    def _precompute(self) -> None:
        """Предрасчёт кумулятивных распределений.

        Attributes:
            transitions: Словарь переходов
            current_state: Исходящее состояние
            next_states: Возможные следующие состояния и их probability
            state: Кумулятивная сумма весов
            state_pool: Дочерние узлы

        Returns:
            self._cum_weights: Ключу состояния присвоен список вероятностей
            self._state_pool: Ключу состояния присвоен список состояний
        """
        for current_state, next_states in self.transitions.items():
            states = list(next_states.keys())
            probs = list(next_states.values())

            cum = []
            acc = 0.0
            for p in probs:
                acc += p
                cum.append(acc)

            self._cum_weights[current_state] = cum
            self._state_pool[current_state] = states

    def _sample_next(self, current: str) -> str:
        """Выбирает следующее состояние по взвешенным вероятностям.

        Attributes:
            current: Исходящее состояние

        Returns:
            pool[idx]: Действие, соответствующее полученному индексу
        """
        if self.transitions[current] == {}:
            logger.debug(f"Проблема: {current} не имеет состояний -> fallback")
            return random.choice(list(self.transitions.keys()))

        cum = self._cum_weights[current]
        pool = self._state_pool[current]

        rand_val = random.uniform(0.0, cum[-1])
        idx = bisect_left(cum, rand_val)
        return pool[idx]

    def generate(
        self,
        start_state: str = LORE_CONTEXT_START,
        length: int = DEFAULT_GENERATION_LENGTH
        ) -> List[str]:
        """Генерирует цепочку состояний.

        Attributes:
            start_state: Исходящее состояние
            length: Длина требуемого списка состояний

        Returns:
            sequence: Список состояний
        """
        if length <= 0:
            return []

        sequence = [start_state]
        current = start_state
        for _ in range(1, length):
            current = self._sample_next(current)
            sequence.append(current)
        return sequence
