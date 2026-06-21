# config/audio_config.py
class SoundKeys:
    PICKUP = "pickup"
    TALK = "talk"
    BGM_THEME = "bgm_theme"
    WIN = "win"
    LOSE = "lose"

SOUND_PATHS = {
    SoundKeys.PICKUP: "assets/sfx/pickup.wav",
    SoundKeys.TALK: "assets/sfx/talk.wav",
    SoundKeys.BGM_THEME: "assets/music/theme.ogg",
    SoundKeys.WIN: "assets/sfx/win.wav",
    SoundKeys.LOSE: "assets/sfx/lose.wav"
}

# Настройки громкости по умолчанию
DEFAULT_SFX_VOLUME = 0.5
DEFAULT_BGM_VOLUME = 0.3

# Параметры плавного затухания музыки (fade)
FADE_DURATION_MS = 500
FADE_STEPS = 20     