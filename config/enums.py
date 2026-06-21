from enum import Enum, auto, IntEnum


class NodeStatus(Enum):
    "Статусы узлов."
    SUCCESS = auto()
    FAILURE = auto()
    RUNNING = auto()


class NPCType(Enum):
    "Виды NPC."
    ATTACKER = "attacker"
    ESCAPER = "escaper"
    STORYTELLER = "storyteller"


class Rarity(Enum):
    """Виды редкостей предметов."""

    COMMON = "Common"
    RARE = "Rare"
    EPIC = "Epic"
    LEGENDARY = "Legendary"
    ANCIENT = "Ancient"


class TileType(IntEnum):
    "Варианты значений игровых тайлов."
    FLOOR = 0
    WALL = 1
