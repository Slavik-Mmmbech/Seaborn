import math
from config.enums import Rarity

# Настройки Lightmap + Raycasting
LIGHT_RADIUS_BASE = 120
EPSILON = 0.0001
MAX_RAY_ITERATIONS = 5000
MIN_MOVE_DISTANCE = 0.1
RAY_ANGLE_STEP = math.radians(5.0)
FULL_CIRCLE = math.tau
SAFE_DIVISION_EPSILON = 1e-9
LIGHT_MASK_MIN = 3
EMPTY = -1

# Константы конфигурации игрока
PLAYER_HEIGHT = 24
PLAYER_WIDTH = 24
PLAYER_MAX_OXYGEN = 100
OXYGEN_DRAIN_PER_SECOND = 2
OXYGEN_CRITICAL_THRESHOLD = 30
INVENTORY_MAX_WEIGHT = 15.0
PLAYER_MOVE_SPEED = 3.0
VALID_DELTA = 2
VALID_SIZE = 4
EXP = 1e-3

# Константы конфигурации shuffle bag для генерации предметов
SHUFFLE_BAG_SIZE = 100
MIN_SUFFLE_BAG_SIZE = 0

# Настройки управления редкостью предметов
LOW_VALUE = 10.0
HIGH_VALUE = 100.0

ITEM_RARITY_CONFIG = {
    Rarity.COMMON:    (0.5, 1.5, 1.0, 0.60),
    Rarity.RARE:      (1.0, 3.5, 6.0,  0.25),
    Rarity.EPIC:      (3.0, 5.0, 15.0, 0.09),
    Rarity.LEGENDARY: (4.5, 8.0, 25.0, 0.04),
    Rarity.ANCIENT:   (7.0, 10.5, 40.0, 0.02)
} 

# Структура ITEM_RARITY_CONFIG: {
    # "Редкость": 
        # (мин.вес, 
        # макс.вес,
        # множитель ценности, 
        # шанс спавна предмета)
    #}

# Константы конфигурации коллекционных предметов
COLLECTIBLES_COUNT = 30
COLLECT_RECT_BORDER_RADIUS = 4
COLLECT_RECT_SIZE = (4, 4, 24, 24) 
COLLECT_RECT_WIDTH = 1

# Константы конфигурации NPC
NPC_MAX_HEALTH = 100
NPC_SPEED = 1.3
NPC_RADIUS = 14
NPC_PATROL_ANGLE = 0.0
NPC_LABEL_FONT_SIZE = 16
NPC_TYPE_MARKER_FONT_SIZE = 18
NPC_DELTA_TIME = 0.016
PATROL_ANGLE_DELTA = 0.03
POS_DELTA = 28
SPEED_PENALTY_FACTOR = 0.5
NPC_ATTACK_RANGE = 28
NPC_SEE_DISTANCE = 120
NPC_TALK_DISTANCE = 50
NPC_COORD = -20
NPC_SPAWN_RANDOM_RANGE = 20
ATTACKER_ROOM_INDICES = slice(2, 4)
ESCAPER_ROOM_INDICES = slice(4, 6)
STORYTELLER_ROOM_START_INDEX = 6
STORYTELLER_MIN_DISTANCE_FROM_ENTRY = 240
STORYTELLER_ROOM_COUNT = 2

# Конфигурация наград за общение с NPC
LOOT_REWARDS = {
                "common_phrase": 0.50,
                "hint": 0.30,
                "rare_lore": 0.1,
                "oxygen_bonus": 0.1
            }

# Настройки уровней
LEVEL_COUNT_TO_COMPLETE = 3
NOTIF_TIME = 3.0

STORYTELLER_OXYGEN_BONUS = 25       # Объем восстанавливаемого кислорода
STORYTELLER_PICKUP_MIN_VAL = 10.0   # Минимальное базовое значение предмета
STORYTELLER_PICKUP_MAX_VAL = 25.0   # Максимальное базовое значение предмета

OXYGEN_REWARD_ON_PICKUP = 5