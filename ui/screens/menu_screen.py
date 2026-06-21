"""Главное меню игры."""
import pygame
import config.display_config as display
from ui.screens.base_screen import BaseScreen


class MenuScreen(BaseScreen):
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)

    def handle_event(self, event: pygame.event.Event) -> str | None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "quit"
            return "start_game"
        if event.type == pygame.MOUSEBUTTONDOWN:
            return "start_game"
        return None

    def draw(self) -> None:
        overlay = pygame.Surface((display.SCREEN_WIDTH, display.SCREEN_HEIGHT))
        overlay.fill(display.MENU_BACKGROUND)
        overlay.set_alpha(display.MENU_ALPHA)
        self.screen.blit(overlay, display.BASE_COORDS)

        title = self.font.render("Seaborn: Explore and collect", True, display.BASE_COLOR)
        title_rect = title.get_rect(center=(display.SCREEN_WIDTH // 2, display.MENU_TITLE_Y))
        self.screen.blit(title, title_rect)

        start = self.small_font.render(
            "Нажмите любую клавишу чтобы начать.", True, display.MENU_TEXT_LIGHT
        )
        start_rect = start.get_rect(center=(display.SCREEN_WIDTH // 2, display.MENU_START_Y))
        self.screen.blit(start, start_rect)