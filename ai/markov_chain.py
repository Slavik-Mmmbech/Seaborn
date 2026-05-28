import random
from bisect import bisect_left
from typing import Dict, List, Tuple
from config import DEFAULT_GENERATION_LENGTH

class MarkovChain:
    """
    Цепь Маркова для генерации тематических текстов.
    """

    def __init__(self, transitions: Dict[str, Dict[str, float]]):
        self.transitions = transitions
        self._cum_weights: Dict[str, List[float]] = {}
        self._state_pool: Dict[str, List[str]] = {}
        self._precompute()

    def _precompute(self) -> None:
        """Предрасчёт кумулятивных распределений для O(log N) семплинга."""
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
        """Выбирает следующее состояние по взвешенным вероятностям."""
        if current not in self.transitions:
            return random.choice(list(self.transitions.keys()))

        cum = self._cum_weights[current]
        pool = self._state_pool[current]
        
        # uniform + bisect_left = бинарный поиск по кумулятивному массиву   
        rand_val = random.uniform(0.0, cum[-1])
        idx = bisect_left(cum, rand_val)
        return pool[idx]

    def generate(self, start_state: str, length: int = DEFAULT_GENERATION_LENGTH) -> List[str]:
        if length <= 0:
            return []
            
        sequence = [start_state]
        current = start_state
        for _ in range(1, length):
            current = self._sample_next(current)
            sequence.append(current)
        return sequence