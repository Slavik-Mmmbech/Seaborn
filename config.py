from entities.item import Rarity

# Настройки отображения игрового экрана
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60
TILE_SIZE = 32

WATER_COLOR = (18, 82, 135)
FOG_COLOR =  (10, 40, 70, 180)
LIGHT_RADIUS_BASE = 120

# Настройки управления редкостью предметов

ITEM_RARITY_CONFIG = {
    Rarity.COMMON:    (0.5, 1.5, 1.0, 0.60),
    Rarity.RARE:      (1.0, 3.5, 6.0,  0.25),
    Rarity.EPIC:      (3.0, 5.0, 15.0, 0.09),
    Rarity.LEGENDARY: (4.5, 8.0, 25.0, 0.04),
    Rarity.ANCIENT:   (7.0, 10.5, 40.0, 0.02)
} 

#Структура ITEM_RARITY_CONFIG: {
    # "Редкость": 
        # (мин.вес, 
        # макс.вес,
        # множитель ценности, 
        # шанс спавна предмета)
    #}
    
ITEM_CATALOG = {
    "pearl": {"rarity": Rarity.RARE, "weight": (1.5, 3.0), "value": 6.0, "description": "Белая сияющая жемчужина"}
}

# Игровые механики

PLAYER_MAX_OXYGEN = 100
OXYGEN_DRAIN_PER_SECOND = 2
INVENTORY_MAX_WEIGHT = 15.0
PLAYER_MOVE_SPEED = 3.0
SHUFFLE_BAG_SIZE = 100

SOUND_VOLUME_MASTER = 0.7

# Настройки BSP генерации

MIN_SIZE = 12

SPLIT_RATIO_MIN = 0.2
SPLIT_RATIO_MAX = 0.8

RATIO_LIMIT = 1.2