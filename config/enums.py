from enum import Enum

class Rarity(Enum):
    """Виды редкостей предметов"""

    COMMON = 'Common'
    RARE = 'Rare'
    EPIC = 'Epic'
    LEGENDARY = 'Legendary'
    ANCIENT = 'Ancient'