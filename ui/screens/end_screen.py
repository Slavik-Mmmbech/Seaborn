"""Экран окончания игры (победа/поражение)."""
import pygame
import config.display_config as display
from ui.screens.base_screen import BaseScreen


class EndScreen(BaseScreen):
    def __init__(self, screen: pygame.Surface, full_collection: list, is_victory: bool):
        super().__init__(screen)
        self.full_collection = full_collection
        self.is_victory = is_victory

    def handle_event(self, event: pygame.event.Event) -> str | None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "quit"
            if event.key == pygame.K_r:
                return "restart"
        if event.type == pygame.MOUSEBUTTONDOWN:
            return "restart"
        return None

    def draw(self) -> None:
        overlay = pygame.Surface((display.SCREEN_WIDTH, display.SCREEN_HEIGHT))
        overlay.fill(display.WIN_BACKGROUND if self.is_victory else display.LOSE_BACKGROUND)
        self.screen.blit(overlay, display.BASE_COORDS)

        center_x = display.SCREEN_WIDTH // 2
        current_y = display.END_START_Y

        title = "Уровень завершен!" if self.is_victory else "Кислород закончился!"
        title_color = display.END_OF_LEVEL_LINE_COLOR if self.is_victory else display.END_OF_OXYGEN_LINE_COLOR

        big_font = pygame.font.Font(None, display.END_TITLE_FONT_SIZE)
        end_text = big_font.render(title, True, title_color)
        self.screen.blit(end_text, (center_x - end_text.get_width() // 2, current_y))
        current_y += display.END_STEP_TITLE

        total_score = sum(item.value for item in self.full_collection)
        score_text = self.font.render(
            f"Общий счет: {int(total_score)}", True, display.GOLD
        )
        self.screen.blit(score_text, (center_x - score_text.get_width() // 2, current_y))
        current_y += display.END_STEP_SCORE

        items_header = self.font.render(
            f"Собранные предметы ({len(self.full_collection)}):",
            True, display.BASE_COLOR,
        )
        self.screen.blit(items_header, (center_x - items_header.get_width() // 2, current_y))
        current_y += display.END_STEP_HEADER

        max_items = display.OVERFLOW_PROTECTION
        for item in self.full_collection[:max_items]:
            rarity_color = display.RARITY_COLORS.get(item.rarity, display.BASE_COLOR)
            item_text = self.small_font.render(
                f"• {item.name} ({item.rarity.value}) - {int(item.value)}",
                True, rarity_color,
            )
            self.screen.blit(
                item_text, (center_x - item_text.get_width() // 2, current_y)
            )
            current_y += display.END_STEP_ITEM

        if len(self.full_collection) > max_items:
            remaining = len(self.full_collection) - max_items
            more_text = self.small_font.render(
                f"... и еще {remaining} предметов", True, display.MORE_ITEMS_COLOR
            )
            self.screen.blit(more_text, (center_x - more_text.get_width() // 2, current_y))
            current_y += display.END_STEP_MORE

        hint = self.font.render("Нажмите R для новой игры", True, display.GREY)
        self.screen.blit(hint, (center_x - hint.get_width() // 2, current_y))