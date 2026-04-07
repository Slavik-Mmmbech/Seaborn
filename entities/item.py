from enum import Enum

class Rarity(Enum):
    """ДОКУМЕНТАЦИЯ"""

    COMMON = 'Common'
    RARE = 'Rare'
    EPIC = 'Epic'
    LEGENDARY = 'Legendary'
    ANCIENT = 'Ancient'


class Item:
    def __init__(self, name: str, rarity: Rarity, weight: float, value: int, description: str = ""):
        self.name = name
        self.rarity = rarity
        self.weight = weight
        self.value = value 
        self.description = description


    def __repr__(self):
        return f"{self.name}/💎 {self.rarity.name} / {self.weight} / {self.value} / Описание: {self.description}"