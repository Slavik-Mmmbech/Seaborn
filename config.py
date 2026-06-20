import math
from entities.items import Rarity

# Настройки отображения игрового экрана
SCREEN_WIDTH = 1324
SCREEN_HEIGHT = 668
FPS = 60
TILE_SIZE = 32

LIGHT_RADIUS_BASE = 120
WATER_COLOR = (15, 50, 128)
FLOOR_COLOR = (146, 196, 222)
WALL_COLOR = (20, 30, 45)
EXIT_COLOR = (0, 255, 100)
PLAYER_COLOR = (128, 0, 128)

# Игровые механики

PLAYER_MAX_OXYGEN = 100
OXYGEN_DRAIN_PER_SECOND = 2
INVENTORY_MAX_WEIGHT = 15.0
PLAYER_MOVE_SPEED = 3.0
SHUFFLE_BAG_SIZE = 100
SOUND_VOLUME_MASTER = 0.7

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

RARITY_COLORS = {
                    Rarity.COMMON:    (200, 200, 200),  # Grey
                    Rarity.RARE:      (100, 150, 255),  # Blue
                    Rarity.EPIC:      (200, 100, 255),  # Purple
                    Rarity.LEGENDARY: (255, 215, 0),    # Gold
                    Rarity.ANCIENT:   (255, 170, 0),    # Orange
                }  

BASE_COLOR = (255, 255, 255)
COLLECT_RECT_VALUE = (4, 4, 24, 24)

# Настройки BSP генерации: 1) Дерево
MIN_SIZE = 24
SPLIT_RATIO_MIN = 0.2
SPLIT_RATIO_MAX = 0.8
RATIO_LIMIT = 1.2

# Настройки BSP генерации: 2) Комнаты
ROOM_MARGIN = 6
ROOM_OFFSET = 2
ROOM_MIN_FILL = 0.3

# Настройки BSP генерации: 3) Коридоры
CORRIDOR_CORNER_PROBABILITY = 0.5

# Настройки Lightmap + Raycasting
FULL_CIRCLE = math.tau

# Настройки Markov Chain
DEFAULT_GENERATION_LENGTH = 5
FALLBACK_STATE = "unknown"


GAME_TRANSITIONS = {
            "submerged_lab": {"corridor": 0.5,
                              "warning": 0.25,
                              "echo":0.25
                              },
            "corridor": {"terminal": 1.0},
            "terminal": {"support": 0.5, "static": 0.5},
            "pressure_chamber": {"echo": 1.0},
            "support": {"warning": 1.0},
            "static": {"static": 0.9, "support": 0.1},
            "alarm": {"support": 1.0},
            "silence": {"distant_drone": 1.0},
            "echo": {"whisper": 1.0},
            "warning": {"silence": 1.0},
            "distant_drone": {"static": 1.0},
            "whisper": {"silence": 1.0}
        }

# Константы конфигурации NPC
NPC_MAX_HEALTH = 100
NPC_SPEED = 1.3
NPC_RADIUS = 14
NPC_PATROL_ANGLE = 0.0
NPC_LABEL_FONT_SIZE = 16
NPC_DELTA_TIME = 0.016
PATROL_ANGLE_DELTA = 0.03
POS_DELTA = 28
NPC_ATTACK_RANGE = 28
NPC_SEE_DISTANCE = 120
NPC_TALK_DISTANCE = 50
LORE_CONTEXT_START = "submerged_lab"
LORE_COOLDOWN_SECONDS = 5.0
LORE_DISPLAY_DURATION = 3.0
LORE_TEXT_LENGTH = 4
LORE_VOCABULARY = {
    "submerged_lab": "Вы находитесь в затонувшей лаборатории.",
    "corridor": "В коридоре поблизости есть награды.",
    "terminal": "В воде содержится терминальное количество урана.",
    "pressure_chamber": "Тут много дронов, рыбы уплыли.",
    "alarm": "Берегись.",
    "echo": "Слышу эхо.",
    "whisper": "Лучше говорить шепотом.",
    "silence": "...",
    "distant_drone": "Удачи.",
    "static": "Связь не работает на такой глубине.",
    "support": "Успейте спастись.",
    "warning": "Вам здесь не рады.",
    "unknown": "[Нераспознанный сигнал]"
}
LOOT_REWARDS = {
                "common_phrase": 0.50,
                "hint": 0.30,
                "rare_lore": 0.1,
                "oxygen_bonus": 0.1
            }

# Настройки уровней
LEVEL_COUNT_TO_COMPLETE = 3
NOTIF_TIME = 3.0

# Настройки Quadtree
MAX_CAPACITY = 4
MAX_DEPTH = 5

# UI кнопки и меню
BUTTON_WIDTH = 180
BUTTON_HEIGHT = 42
BUTTON_COLOR = (33, 148, 243)
BUTTON_HOVER_COLOR = (50, 180, 255)
BUTTON_TEXT_COLOR = (255, 255, 255)
MENU_BACKGROUND = (8, 24, 52)
PAUSE_OVERLAY = (0, 0, 0, 160)

# Тестирование 
COLOR_BG = (30, 30, 40)
COLOR_BOUNDARY = (60, 60, 70)
COLOR_OBJECT = (70, 130, 180)
COLOR_QUERY = (255, 100, 100, 50)
COLOR_HIT = (255, 215, 0)
MAX_ENTITIES = 150
ENTITY_RADIUS = 4

TEXT_COLOR = (255, 255, 255)
ACCENT_COLOR = (0, 255, 150)
BORDER_COLOR = (100, 100, 120)

FONT_SIZE_HEADER = 28
FONT_SIZE_SMALL = 18
FONT_FAMILY = "consolas"

CELL_PADDING = 15
SEQUENCE_GAP = 12
LINE_HEIGHT = 30