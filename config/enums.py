from enum import Enum, auto, IntEnum

class NodeStatus(Enum):
    SUCCESS = auto()
    FAILURE = auto()
    RUNNING = auto()

class NPCType(Enum):
    ATTACKER = "attacker"
    ESCAPER = "escaper"
    STORYTELLER = "storyteller"

class Rarity(Enum):
    """Виды редкостей предметов"""

    COMMON = 'Common'
    RARE = 'Rare'
    EPIC = 'Epic'
    LEGENDARY = 'Legendary'
    ANCIENT = 'Ancient'

class TileType(IntEnum):
    FLOOR = 0
    WALL = 1
