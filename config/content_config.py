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