"""Настройки игрового окна"""
from config.enums import Rarity

# Настройки отображения игрового экрана
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 568
FPS = 60
TILE_SIZE = 32

WATER_COLOR = (15, 50, 128)
FLOOR_COLOR = (146, 196, 222)
WALL_COLOR = (20, 30, 45)
EXIT_COLOR = (0, 255, 100)
PLAYER_COLOR = (128, 0, 128)

SOUND_VOLUME_MASTER = 0.7
# Игровые механики

RARITY_COLORS = {
    Rarity.COMMON: (200, 200, 200),  # Grey
    Rarity.RARE: (100, 150, 255),  # Blue
    Rarity.EPIC: (200, 100, 255),  # Purple
    Rarity.LEGENDARY: (255, 215, 0),    # Gold
    Rarity.ANCIENT: (255, 170, 0),    # Orange
                }  

BASE_COLOR = (255, 255, 255)

# UI кнопки и меню
BUTTON_WIDTH = 180
BUTTON_HEIGHT = 42
BUTTON_COLOR = (33, 148, 243)
BUTTON_HOVER_COLOR = (50, 180, 255)
BUTTON_TEXT_COLOR = (255, 255, 255)
MENU_BACKGROUND = (8, 24, 52)
PAUSE_OVERLAY = (0, 0, 0, 160)

# Тестирование 
# COLOR_BG = (30, 30, 40)
# COLOR_BOUNDARY = (60, 60, 70)
# COLOR_OBJECT = (70, 130, 180)
# COLOR_QUERY = (255, 100, 100, 50)
# COLOR_HIT = (255, 215, 0)
# MAX_ENTITIES = 150
# ENTITY_RADIUS = 4

# TEXT_COLOR = (255, 255, 255)
# ACCENT_COLOR = (0, 255, 150)
# BORDER_COLOR = (100, 100, 120)

# FONT_SIZE_HEADER = 28
# FONT_SIZE_SMALL = 18
# FONT_FAMILY = "consolas"

# CELL_PADDING = 15
# SEQUENCE_GAP = 12
# LINE_HEIGHT = 30