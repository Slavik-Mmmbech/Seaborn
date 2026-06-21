# core/audio_manager.py
"""
Менеджер аудио. Отвечает за загрузку, воспроизведение и микширование звуков.
Спроектирован по принципу единственной ответственности (SRP).
"""
import pygame
from config import audio_config as cfg
from config.logging_config import setup_logger

logger = setup_logger(__name__)


class AudioManager:
    """
    Централизованное управление звуками.
    Использует pygame.mixer для SFX и pygame.mixer.music для BGM.
    """

    def __init__(self) -> None:
        pygame.mixer.init()
        self._sounds: dict[str, pygame.mixer.Sound] = {}
        
        # Флаги включения/выключения (для меню паузы)
        self.sfx_enabled: bool = True
        self.bgm_enabled: bool = True
        
        self._load_all_sounds()
        logger.info("AudioManager инициализирован.")

    def _load_all_sounds(self) -> None:
        """Загружает все SFX из конфига в словарь."""
        for key, path in cfg.SOUND_PATHS.items():
            if key == cfg.SoundKeys.BGM_THEME:
                continue
            try:
                self._sounds[key] = pygame.mixer.Sound(path)
                self._sounds[key].set_volume(cfg.DEFAULT_SFX_VOLUME)
            except pygame.error as e:
                logger.warning(f"Не удалось загрузить звук '{key}': {e}")

    def play_sfx(self, sound_key: str) -> None:
        """Воспроизводит звуковой эффект, если SFX включены."""
        if not self.sfx_enabled:
            return
        sound = self._sounds.get(sound_key)
        if sound is not None:
            sound.play()

    def play_bgm(self, sound_key: str, loops: int = -1) -> None:
        """Запускает фоновую музыку с бесконечным циклом."""
        if not self.bgm_enabled:
            return
        path = cfg.SOUND_PATHS.get(sound_key)
        if path is None:
            return
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(cfg.DEFAULT_BGM_VOLUME)
            pygame.mixer.music.play(loops)
        except pygame.error as e:
            logger.warning(f"Не удалось запустить BGM: {e}")

    def stop_bgm(self) -> None:
        """Останавливает фоновую музыку."""
        pygame.mixer.music.stop()

    def pause_bgm(self) -> None:
        """Ставит BGM на паузу (без потери позиции)."""
        pygame.mixer.music.pause()

    def unpause_bgm(self) -> None:
        """Снимает BGM с паузы."""
        pygame.mixer.music.unpause()

    def toggle_sfx(self) -> bool:
        """Переключает SFX. Возвращает новое состояние."""
        self.sfx_enabled = not self.sfx_enabled
        logger.info(f"SFX: {'ON' if self.sfx_enabled else 'OFF'}")
        return self.sfx_enabled

    def toggle_bgm(self) -> bool:
        """
        Переключает BGM. Если выключаем — ставим на паузу,
        если включаем — снимаем с паузы.
        """
        self.bgm_enabled = not self.bgm_enabled
        if self.bgm_enabled:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()
        logger.info(f"BGM: {'ON' if self.bgm_enabled else 'OFF'}")
        return self.bgm_enabled

    def fade_out_bgm(self) -> None:
        """
        Плавно уменьшает громкость BGM до 0 за FADE_DURATION_MS.
        """
        if not pygame.mixer.music.get_busy():
            return
        start_volume = pygame.mixer.music.get_volume()
        step_duration = cfg.FADE_DURATION_MS // cfg.FADE_STEPS
        for i in range(cfg.FADE_STEPS, -1, -1):
            volume = start_volume * (i / cfg.FADE_STEPS)
            pygame.mixer.music.set_volume(max(0.0, volume))
            pygame.time.delay(step_duration)
        pygame.mixer.music.stop()

    def fade_in_bgm(self, sound_key: str) -> None:
        """Плавно увеличивает громкость BGM от 0 до DEFAULT_BGM_VOLUME."""
        self.play_bgm(sound_key)
        pygame.mixer.music.set_volume(0.0)
        step_duration = cfg.FADE_DURATION_MS // cfg.FADE_STEPS
        for i in range(cfg.FADE_STEPS + 1):
            volume = cfg.DEFAULT_BGM_VOLUME * (i / cfg.FADE_STEPS)
            pygame.mixer.music.set_volume(volume)
            pygame.time.delay(step_duration)