import pytest
import random
from ai import MarkovChain

@pytest.fixture
def simple_transitions():
    """Фикстура с известным графом переходов."""
    return {
        "A": {"B": 0.3, "C": 0.7},
        "B": {"A": 0.5, "C": 0.5},
        "C": {"A": 1.0}
    }

@pytest.fixture
def chain(simple_transitions):
    return MarkovChain(simple_transitions)

# Проверка длины и начального состояния
def test_generate_length_and_start(chain):
    result = chain.generate("A", length=5)
    assert len(result) == 5
    assert result[0] == "A"

# Граничное условие
def test_generate_zero_length(chain):
    assert chain.generate("A", length=0) == []
    assert chain.generate("A", length=-3) == []

# 4. Проверка кумулятивных весов (детерминированный мок)
def test_sample_next_deterministic(chain, monkeypatch):
    monkeypatch.setattr(random, "uniform", lambda a, b: 0.1)
    assert chain._sample_next("A") == "B"  # 0.1 < 0.3

# 5. Статистическая проверка распределения
def test_sampling_probabilities(chain):
    random.seed(42)  # Воспроизводимость результата
    counts = {"B": 0, "C": 0}
    for _ in range(5000):
        next_state = chain._sample_next("A")
        counts[next_state] += 1
    total = sum(counts.values())
    assert counts["B"] / total == pytest.approx(0.3, abs=0.05)
    assert counts["C"] / total == pytest.approx(0.7, abs=0.05)