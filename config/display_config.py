"""Настройки игрового окна"""
from config.enums import Rarity

# Настройки отображения игрового экрана
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
FPS = 60
TILE_SIZE = 32

WATER_COLOR = (15, 50, 128)
FLOOR_COLOR = (146, 196, 252)
WALL_COLOR = (20, 30, 45)
EXIT_COLOR = (0, 255, 100)
PLAYER_COLOR = (128, 0, 128)
CORRIDOR_COLOR = (140, 140, 220)
CORRIDOR_WIDTH = 16
WALL_THICKNESS = 4

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