from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Callable

# Статусы узлов
class NodeStatus(Enum):
    SUCCESS = auto()
    FAILURE = auto()
    RUNNING = auto()

class Blackboard:
    """
    Shared state storage (Blackboard pattern).
    Позволяет узлам дерева обмениваться данными без прямой зависимости друг от друга.
    """
    def __init__(self):
        self._data: Dict[str, Any] = {}

    def get(self, key: str) -> Any:
        return self._data.get(key)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def has(self, key: str) -> bool:
        return key in self._data

class BTNode(ABC):
    """Базовый класс узла дерева поведения (Open/Closed Principle)."""
    @abstractmethod
    def tick(self, blackboard: Blackboard) -> NodeStatus:
        pass

class Sequence(BTNode):
    """Возвращает SUCCESS только если ВСЕ дочерние узлы успешны."""
    def __init__(self, children: List[BTNode]):
        self.children = children

    def tick(self, blackboard: Blackboard) -> NodeStatus:
        for child in self.children:
            status = child.tick(blackboard)
            if status != NodeStatus.SUCCESS:
                return status  # Остановка при первой ошибке
        return NodeStatus.SUCCESS

class Selector(BTNode):
    """Возвращает SUCCESS при первом успешном дочернем узле."""
    def __init__(self, children: List[BTNode]):
        self.children = children

    def tick(self, blackboard: Blackboard) -> NodeStatus:
        for child in self.children:
            status = child.tick(blackboard)
            if status != NodeStatus.FAILURE:
                return status  # Остановка при первом успехе
        return NodeStatus.FAILURE

class Condition(BTNode):
    """Проверяет предикат. Не меняет состояние мира."""
    def __init__(self, predicate: Callable[[Blackboard], bool]):
        self.predicate = predicate

    def tick(self, blackboard: Blackboard) -> NodeStatus:
        return NodeStatus.SUCCESS if self.predicate(blackboard) else NodeStatus.FAILURE

class Action(BTNode):
    """Выполняет действие (перемещение, атака, сбор лута)."""
    def __init__(self, behavior_fn: Callable[[Blackboard], NodeStatus]):
        self.behavior_fn = behavior_fn

    def tick(self, blackboard: Blackboard) -> NodeStatus:
        return self.behavior_fn(blackboard)