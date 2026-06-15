from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any, Dict, List, Callable

# Статусы узлов
class NodeStatus(Enum):
    SUCCESS = auto()
    FAILURE = auto()
    RUNNING = auto()

class Blackboard:
    """
    Общее хранилище состояний.
    """
    def __init__(self):
        self._data: Dict[str, Any] = {}

    def get(self, key: str) -> Any:
        """Получение значения ключа в словаре"""
        return self._data.get(key)

    def set(self, key: str, value: Any) -> None:
        """Установка значения ключа в словарь/добавление ключа в словарь"""
        self._data[key] = value

    def has(self, key: str) -> bool:
        """Проверка наличия ключа в словаре"""
        return key in self._data

class BTNode(ABC):
    """Базовый класс узла дерева поведения."""
    @abstractmethod
    def tick(self, blackboard: Blackboard) -> NodeStatus:
        pass

class Sequence(BTNode):
    """Узел, выполняющий дочерние узлы строго по порядку.
    
    Attributes:
        children: Список узлов
    Returns:
        При нарушении условий узла:
            status: Состояние дерева поведения в данный момент.
        При успешном выполнении:
            NodeStatus.SUCCESS
    """
    def __init__(self, children: List[BTNode]):
        self.children = children

    def tick(self, blackboard: Blackboard) -> NodeStatus:
        for child in self.children:
            status = child.tick(blackboard)
            if status != NodeStatus.SUCCESS:
                return status  # Остановка при первой ошибке
        return NodeStatus.SUCCESS

class Selector(BTNode):
    """Узел, который перебирает варианты, пока не найдет работающий.
    
    Attributes:
        children: Список узлов
    Returns:
        При нарушении условий узла:
            NodeStatus.FAILURE
        При успешном выполнении:
            status: Состояние дерева поведения в данный момент.
    """
    def __init__(self, children: List[BTNode]):
        self.children = children

    def tick(self, blackboard: Blackboard) -> NodeStatus:
        for child in self.children:
            status = child.tick(blackboard)
            if status != NodeStatus.FAILURE:
                return status  # Остановка при первом успехе
        return NodeStatus.FAILURE

class Condition(BTNode):
    """ Узел-проверка наи соотвествие условию

    Attributes:
        predicate: Функция, передающая состояние проверки
    Returns:
        При нарушении условий проверки:
            NodeStatus.FAILURE
        При выполнении условий:
            NodeStatus.SUCCESS
    """
    def __init__(self, predicate: Callable[[Blackboard], bool]):
        self.predicate = predicate

    def tick(self, blackboard: Blackboard) -> NodeStatus:
        return NodeStatus.SUCCESS if self.predicate(blackboard) else NodeStatus.FAILURE

class Action(BTNode):
    """Узел, выполняющий действие.
    
    Attributes:
        behavior_fn: Функция поведения при инициализации
    Returns:
        NodeStatus 
    """
    def __init__(self, behavior_fn: Callable[[Blackboard], NodeStatus]):
        self.behavior_fn = behavior_fn

    def tick(self, blackboard: Blackboard) -> NodeStatus:
        return self.behavior_fn(blackboard)