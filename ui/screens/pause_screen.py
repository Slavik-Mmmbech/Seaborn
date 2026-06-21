"""Экран паузы."""
import pygame
from typing import Callable

import config.display_config as display
from ui.screens.base_screen import BaseScreen


class PauseScreen(BaseScreen):
    def __init__(self, screen: pygame.Surface, audio_manager):
        super().__init__(screen)
        self.audio_manager = audio_manager
        self._calculate_score: Callable | None = None  # Зарезервировано для будущих вычислений

    def handle_event(self, event: pygame.event.Event) -> str | None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "resume"
            if event.key == pygame.K_m:
                self.audio_manager.toggle_bgm()
            if event.key == pygame.K_s:
                self.audio_manager.toggle_sfx()
        return None

    def draw(self, score: int = 0) -> None:
        overlay = pygame.Surface(
            (display.SCREEN_WIDTH, display.SCREEN_HEIGHT), pygame.SRCALPHA
        )
        overlay.fill(display.PAUSE_OVERLAY)
        self.screen.blit(overlay, display.BASE_COORDS)

        center_x = display.SCREEN_WIDTH // 2

        paused_text = self.font.render("Пауза", True, display.BASE_COLOR)
        self.screen.blit(
            paused_text,
            (center_x - paused_text.get_width() // 2, display.SCREEN_HEIGHT // 2 - display.PAUSE_TEXT_Y_OFFSET),
        )

        resume_text = self.small_font.render(
            "Нажмите ESC чтобы продолжить", True, display.MENU_TEXT_LIGHT
        )
        self.screen.blit(
            resume_text,
            (center_x - resume_text.get_width() // 2, display.SCREEN_HEIGHT // 2 + display.PAUSE_TEXT_Y_OFFSET),
        )

        score_text = self.font.render(
            f"Нынешний счет: {int(score)}", True, display.BASE_COLOR
        )
        self.screen.blit(
            score_text, (center_x - score_text.get_width() // 2, display.PAUSE_SCORE_Y)
        )

        sfx_status = "ВКЛ" if self.audio_manager.sfx_enabled else "ВЫКЛ"
        bgm_status = "ВКЛ" if self.audio_manager.bgm_enabled else "ВЫКЛ"
        audio_info = self.small_font.render(
            f"[M] Музыка: {bgm_status}    [S] Звуки: {sfx_status}",
            True, display.GREY,
        )
        self.screen.blit(
            audio_info, (center_x - audio_info.get_width() // 2, display.PAUSE_AUDIO_Y)
        )