"""
Модуль реализации дерева поведения (Behavior Tree).

Предоставляет базовые компоненты для построения деревьев поведения:
- Blackboard: общее хранилище состояний
- CompositeNode: базовый класс для узлов с детьми
- Sequence: последовательное выполнение детей
- Selector: выбор первого успешного ребёнка
- Condition: проверка условия
- Action: выполнение действия

Алгоритм обхода дерева: O(n) где n - количество узлов в дереве.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Callable

from config.enums import NodeStatus


class Blackboard:
    """
    Общее хранилище состояний для обмена данными между узлами дерева.
    
    Реализует паттерн Blackboard - централизованное хранилище данных,
    доступное всем узлам дерева поведения.
    
    Attributes:
        _data: Внутренний словарь для хранения пар ключ-значение.
    
    Example:
        >>> bb = Blackboard()
        >>> bb.set("health", 100)
        >>> bb.get("health")
        100
    """
    
    def __init__(self):
        """Инициализирует пустое хранилище состояний."""
        self._data: Dict[str, Any] = {}
    
    def get(self, key: str) -> Any:
        """
        Получение значения по ключу.
        
        Args:
            key: Ключ для поиска значения.
            
        Returns:
            Значение по ключу или None, если ключ не найден.
        """
        return self._data.get(key)
    
    def set(self, key: str, value: Any) -> None:
        """
        Установка или обновление значения по ключу.
        
        Args:
            key: Ключ для установки значения.
            value: Значение для сохранения.
        """
        self._data[key] = value
    
    def has(self, key: str) -> bool:
        """
        Проверка наличия ключа в хранилище.
        
        Args:
            key: Ключ для проверки.
            
        Returns:
            True, если ключ существует, иначе False.
        """
        return key in self._data


class BTNode(ABC):
    """
    Базовый абстрактный класс узла дерева поведения.
    
    Все узлы дерева должны наследоваться от этого класса
    и реализовывать метод tick().
    """
    
    @abstractmethod
    def tick(self, blackboard: Blackboard) -> NodeStatus:
        """
        Выполнение одного шага узла.
        
        Args:
            blackboard: Общее хранилище состояний.
            
        Returns:
            Статус выполнения узла (SUCCESS, FAILURE, RUNNING).
        """
        pass


class CompositeNode(BTNode, ABC):
    """
    Базовый класс для композитных узлов (имеющих дочерние узлы).
    
    Реализует паттерн Composite - единый интерфейс для работы
    с одиночными узлами и их композициями.
    
    Attributes:
        children: Список дочерних узлов.
    """
    
    def __init__(self, children: List[BTNode]):
        """
        Инициализация композитного узла.
        
        Args:
            children: Список дочерних узлов (должен быть непустым).
            
        Raises:
            ValueError: Если список детей пуст.
        """
        if not children:
            raise ValueError("CompositeNode requires at least one child")
        self.children = children
    
    @abstractmethod
    def _should_stop(self, status: NodeStatus) -> bool:
        """
        Определение условия остановки обхода детей.
        
        Args:
            status: Статус, возвращённый текущим ребёнком.
            
        Returns:
            True, если нужно прервать обход, иначе False.
        """
        pass
    
    @abstractmethod
    def _fallback_status(self) -> NodeStatus:
        """
        Возвращаемый статус, если ни один ребёнок не сработал.
        
        Returns:
            Статус по умолчанию.
        """
        pass
    
    def tick(self, blackboard: Blackboard) -> NodeStatus:
        """
        Обход дочерних узлов согласно логике композита.
        
        Сложность: O(n), где n - количество детей.
        
        Args:
            blackboard: Общее хранилище состояний.
            
        Returns:
            Статус выполнения композитного узла.
        """
        for child in self.children:
            status = child.tick(blackboard)
            if self._should_stop(status):
                return status
        return self._fallback_status()


class Sequence(CompositeNode):
    """
    Узел последовательного выполнения.
    
    Выполняет дочерние узлы строго по порядку.
    Прерывается при первом FAILURE.
    Возвращает SUCCESS только если все дети успешны.
    
    Логика:
        - Если ребёнок вернул FAILURE → вернуть FAILURE
        - Если все дети SUCCESS → вернуть SUCCESS
    """
    
    def _should_stop(self, status: NodeStatus) -> bool:
        """Остановка при первом FAILURE."""
        return status != NodeStatus.SUCCESS
    
    def _fallback_status(self) -> NodeStatus:
        """Все дети успешны."""
        return NodeStatus.SUCCESS


class Selector(CompositeNode):
    """
    Узел выбора первого успешного варианта.
    
    Перебирает дочерние узлы до первого SUCCESS.
    Прерывается при первом SUCCESS.
    Возвращает FAILURE только если все дети провалились.
    
    Логика:
        - Если ребёнок вернул SUCCESS → вернуть SUCCESS
        - Если все дети FAILURE → вернуть FAILURE
    """
    
    def _should_stop(self, status: NodeStatus) -> bool:
        """Остановка при первом SUCCESS."""
        return status != NodeStatus.FAILURE
    
    def _fallback_status(self) -> NodeStatus:
        """Все дети провалились."""
        return NodeStatus.FAILURE


class Condition(BTNode):
    """
    Узел-условие (лист дерева).
    
    Проверяет предикат и возвращает соответствующий статус.
    
    Attributes:
        predicate: Функция-предикат, принимающая Blackboard.
    """
    
    def __init__(self, predicate: Callable[[Blackboard], bool]):
        """
        Инициализация узла-условия.
        
        Args:
            predicate: Функция, возвращающая True/False.
        """
        self.predicate = predicate
    
    def tick(self, blackboard: Blackboard) -> NodeStatus:
        """
        Проверка условия.
        
        Сложность: O(1) (зависит от сложности предиката).
        
        Args:
            blackboard: Общее хранилище состояний.
            
        Returns:
            SUCCESS если предикат истинен, иначе FAILURE.
        """
        return NodeStatus.SUCCESS if self.predicate(blackboard) else NodeStatus.FAILURE


class Action(BTNode):
    """
    Узел-действие (лист дерева).
    
    Выполняет переданную функцию поведения.
    
    Attributes:
        behavior_fn: Функция, выполняющая действие.
    """
    
    def __init__(self, behavior_fn: Callable[[Blackboard], NodeStatus]):
        """
        Инициализация узла-действия.
        
        Args:
            behavior_fn: Функция, возвращающая NodeStatus.
        """
        self.behavior_fn = behavior_fn
    
    def tick(self, blackboard: Blackboard) -> NodeStatus:
        """
        Выполнение действия.
        
        Сложность: O(1) (зависит от сложности функции).
        
        Args:
            blackboard: Общее хранилище состояний.
            
        Returns:
            Статус, возвращённый функцией поведения.
        """
        return self.behavior_fn(blackboard)