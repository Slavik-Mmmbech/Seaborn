"""Главный интерфейс игры (HUD). Использует паттерн Композиция."""
import pygame
import config.display_config as display
from ui.components.dialog_box import DialogBox
from ui.components.notification import Notification
from ui.components.hints_panel import HintsPanel
from ui.components.oxygen_bar import OxygenBar


class HUD:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.small_font = pygame.font.Font(None, 24)

        # Инициализация компонентов
        self.oxygen_bar = OxygenBar()
        self.dialog_box = DialogBox(display.SCREEN_WIDTH, display.SCREEN_HEIGHT)
        self.notification = Notification()
        self.hints_panel = HintsPanel()

    def draw(self, world) -> None:
        """Отрисовывает все элементы HUD на основе состояния мира."""
        if not world.player:
            return

        self._draw_player_stats(world.player)
        self.notification.draw(self.screen, world.notification_message)
        self._draw_exit_prompt(world.player_in_exit_zone)
        self.hints_panel.draw(self.screen, display.SCREEN_WIDTH - 150, 10)
        self._draw_dialog(world)

    def _draw_player_stats(self, player) -> None:
        """Отрисовывает кислород и инвентарь."""
        self.oxygen_bar.draw(self.screen, player.oxygen)
        self._draw_inventory(player)

    def _draw_inventory(self, player) -> None:
        if not hasattr(player, "inventory"):
            return

        inv = player.inventory
        text = self.small_font.render(
            f"Вес: {inv.current_weight:.1f}/{inv.max_weight} | Предметов: {len(inv)}",
            True, display.BASE_COLOR,
        )
        self.screen.blit(text, (10, 40))

        y_offset = 70
        max_visible = (display.SCREEN_HEIGHT // 2 - y_offset) // 22

        for i, item in enumerate(inv):
            if i >= max_visible:
                remaining = len(inv) - max_visible
                more = self.small_font.render(f"+ {remaining} ещё...", True, (150, 150, 150))
                self.screen.blit(more, (10, y_offset))
                break

            color = display.RARITY_COLORS.get(item.rarity, display.BASE_COLOR)
            item_text = self.small_font.render(
                f"• {item.name} ({item.rarity.value})", True, color
            )
            self.screen.blit(item_text, (10, y_offset))
            y_offset += 22

    def _draw_exit_prompt(self, in_zone: bool) -> None:
        if not in_zone:
            return
        font = pygame.font.Font(None, 28)
        text = font.render("Нажмите R: Завершить уровень?", True, (100, 255, 100))
        rect = text.get_rect(center=(display.SCREEN_WIDTH // 2, display.SCREEN_HEIGHT - 100))
        
        pygame.draw.rect(self.screen, (50, 100, 50), rect.inflate(20, 10))
        pygame.draw.rect(self.screen, (100, 255, 100), rect.inflate(20, 10), 2)
        self.screen.blit(text, rect)

    def _draw_dialog(self, world) -> None:
        if world.active_storyteller and world.talk_text:
            self.dialog_box.draw(self.screen, world.talk_text)
        elif world.storyteller_in_range:
            prompt = self.small_font.render(
                "Нажмите E: Говорить", True, display.BASE_COLOR
            )
            self.screen.blit(
                prompt,
                (display.SCREEN_WIDTH // 2 - prompt.get_width() // 2,
                 display.SCREEN_HEIGHT - 60),
            )