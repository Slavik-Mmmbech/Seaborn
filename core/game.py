import pygame
import config as settings
from core.world import World


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        )
        pygame.display.set_caption("Seaborn")
        self.clock = pygame.time.Clock()
        self.world = World()
        self.world.generate()
        self.debug_mode = True
        self.running = True
        self.paused = False
        self.show_menu = True
        self.show_end_screen = False
        self.levels_completed = 0

    def _reset_game(self):
        self.levels_completed = 0
        self.world.generate()
        self.paused = False
        self.show_menu = False
        self.show_end_screen = False

    def run(self):
        while self.running:
            self.clock.tick(settings.FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_l:
                        self.debug_mode = not self.debug_mode
                    elif event.key == pygame.K_ESCAPE:
                        if self.show_menu or self.show_end_screen:
                            self.running = False
                        else:
                            self.paused = not self.paused
                    elif event.key == pygame.K_r:
                        if self.show_menu or self.show_end_screen:
                            self._reset_game()
                        elif self.world.player and self.world.player.oxygen <= 0:
                            self._reset_game()
                        elif self.world.player_in_exit_zone:
                            if self.world.player.inventory:
                                score = self.world.player.calculate_score()
                                print(f"Успешное возвращение! Score: {score}")
                                print(
                                    f"Собрано предметов: {len(self.world.player.inventory)}"
                                )
                            self.world.level_complete = True
                        else:
                            self.world.generate()
                    elif event.key == pygame.K_SPACE and self.world.active_storyteller:
                        self.world.active_storyteller = None
                        self.world.talk_text = ""
                    elif event.key == pygame.K_e:
                        if self.world.active_storyteller:
                            self.world.active_storyteller = None
                            self.world.talk_text = ""
                        else:
                            storyteller = self.world.get_nearby_storyteller()
                            if storyteller:
                                self.world.active_storyteller = storyteller
                                lore_text, reward = storyteller.talk()

                                # Обрабатываем награду
                                if reward == "oxygen_bonus":
                                    if self.world.player:
                                        self.world.player.oxygen = min(
                                            self.world.player.oxygen + 25,
                                            settings.PLAYER_MAX_OXYGEN,
                                        )
                                    self.world.talk_text = f"⭐ {lore_text}\n\n\n\n [ДРЕВНИЙ ДУХ ДАРУЕТ BОЗДУХ! +25 O₂]"
                                elif reward == "rare_lore":
                                    self.world.talk_text = (
                                        f"📜 {lore_text}\n\n  [РЕДКАЯ ИСТОРИЯ]"
                                    )
                                elif reward == "hint":
                                    self.world.talk_text = (
                                        f"💡 {lore_text}\n\n  [ПОДСКАЗКА]"
                                    )
                                else:
                                    self.world.talk_text = lore_text

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.show_menu:
                        self.show_menu = False
                    elif self.show_end_screen:
                        self._reset_game()

            keys = pygame.key.get_pressed()

            if not self.show_menu and not self.paused and not self.show_end_screen:
                self.world.update(keys)
                if self.world.player and self.world.player.oxygen <= 0:
                    self.show_end_screen = True
                if self.world.level_complete:
                    self.levels_completed += 1
                    self.world.level_complete = False
                    if self.levels_completed >= settings.LEVEL_COUNT_TO_COMPLETE:
                        self.show_end_screen = True
                    else:
                        self.world.generate()

            self.screen.fill(settings.WATER_COLOR)
            if not self.show_menu:
                self.world.draw(self.screen)
            self.draw_ui(self.screen)
            pygame.display.flip()

        pygame.quit()

    def _draw_collected_items(self, screen, player, small_font, x_pos, y_offset):
        """Helper method to display collected items with rarity colors"""
        rarity_colors = settings.RARITY_COLORS

        if not hasattr(player, "inventory") or not player.inventory:
            return y_offset

        for item in player.inventory[:5]:
            rarity_color = rarity_colors.get(item.rarity, settings.BASE_COLOR)
            item_text = small_font.render(
                f"• {item.name} ({item.rarity.value})", True, rarity_color
            )
            screen.blit(item_text, (x_pos, y_offset))
            y_offset += 20

        if len(player.inventory) > 5:
            more_text = small_font.render(
                f"+ {len(player.inventory) - 5} more items", True, (150, 150, 150)
            )
            screen.blit(more_text, (x_pos, y_offset))
            y_offset += 20

        return y_offset

    def draw_ui(self, screen):
        """Отрисовка интерфейса"""
        font = pygame.font.Font(None, 36)
        small_font = pygame.font.Font(None, 24)

        if self.show_menu:
            self._draw_menu(screen, font, small_font)
            return

        if self.show_end_screen:
            self._draw_end_screen(screen, font, small_font)
            return

        if self.paused:
            self._draw_pause_overlay(screen, font, small_font)

        if self.world.player:
            oxygen = self.world.player.oxygen
            oxygen_color = settings.BASE_COLOR if oxygen > 30 else (255, 100, 0)
            oxygen_text = font.render(f"Кислород: {int(oxygen)}", True, oxygen_color)
            screen.blit(oxygen_text, (10, 10))

            if hasattr(self.world.player, "inventory"):
                inv_count_text = small_font.render(
                    f"Items: {len(self.world.player.inventory)} (Weight: {self.world.player.current_weight:.1f}/{self.world.player.max_weight})",
                    True,
                    settings.BASE_COLOR,
                )
                screen.blit(inv_count_text, (10, 50))

                y_offset = 70

                for item in self.world.player.inventory:
                    rarity_color = settings.RARITY_COLORS.get(
                        item.rarity, settings.BASE_COLOR
                    )
                    item_text = small_font.render(
                        f"• {item.name} ({item.rarity.value})", True, rarity_color
                    )
                    screen.blit(item_text, (10, y_offset))
                    y_offset += 22

                    if y_offset > settings.SCREEN_HEIGHT // 2:
                        remaining = (
                            len(self.world.player.inventory) - (y_offset - 70) // 22
                        )
                        if remaining > 0:
                            more_text = small_font.render(
                                f"+ {remaining} more items", True, (150, 150, 150)
                            )
                            screen.blit(more_text, (10, y_offset))
                        break

        # Сообщение об отсутствия места
        if self.world.notification_message:
            notification_font = pygame.font.Font(None, 28)
            notification_text = notification_font.render(
                self.world.notification_message, True, (255, 100, 100)
            )
            notification_rect = notification_text.get_rect(
                center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 - 100)
            )
            screen.blit(notification_text, notification_rect)

        # Display level complete prompt when in exit zone
        if self.world.player_in_exit_zone:
            exit_prompt_font = pygame.font.Font(None, 28)
            exit_text = exit_prompt_font.render(
                "Нажмите R: Завершить уровень?", True, (100, 255, 100)
            )
            exit_rect = exit_text.get_rect(
                center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT - 100)
            )
            pygame.draw.rect(screen, (50, 100, 50), exit_rect.inflate(20, 10))
            pygame.draw.rect(screen, (100, 255, 100), exit_rect.inflate(20, 10), 2)
            screen.blit(exit_text, exit_rect)

        hints = [
            "WASD/Arrows - Move",
            "E - Talk when near storyteller",
            "R - Regenerate",
            "D - Debug mode",
            "ESC - Pause/Quit",
        ]
        for i, hint in enumerate(hints):
            text = small_font.render(hint, True, (200, 200, 200))
            screen.blit(text, (settings.SCREEN_WIDTH - 220, 10 + i * 20))

        if self.world.active_storyteller and self.world.talk_text:
            talk_box = pygame.Rect(
                70, settings.SCREEN_HEIGHT - 160, settings.SCREEN_WIDTH - 140, 120
            )
            pygame.draw.rect(screen, (0, 0, 0), talk_box)
            pygame.draw.rect(screen, settings.BASE_COLOR, talk_box, 2)
            rendered = small_font.render(
                "Нажмите SPACE или E чтобы закрыть", True, settings.BASE_COLOR
            )
            screen.blit(rendered, (talk_box.x + 10, talk_box.y + 10))
            self._render_wrapped_text(
                screen,
                self.world.talk_text,
                pygame.Rect(
                    talk_box.x + 10,
                    talk_box.y + 40,
                    talk_box.width - 20,
                    talk_box.height - 50,
                ),
                small_font,
                (220, 220, 220),
            )
        elif self.world.storyteller_in_range:
            prompt = small_font.render(
                "Нажмите E чтобы говорить с storyteller", True, settings.BASE_COLOR
            )
            screen.blit(
                prompt,
                (
                    settings.SCREEN_WIDTH // 2 - prompt.get_width() // 2,
                    settings.SCREEN_HEIGHT - 60,
                ),
            )

    def _render_wrapped_text(self, screen, text, rect, font, color):
        words = text.split(" ")
        lines = []
        current_line = ""

        for word in words:
            if current_line:
                test_line = current_line + " " + word
            else:
                test_line = word

            if font.size(test_line)[0] <= rect.width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        y = rect.y
        for line in lines:
            rendered = font.render(line, True, color)
            screen.blit(rendered, (rect.x, y))
            y += font.get_linesize()
            if y > rect.bottom:
                break

    def _draw_menu(self, screen, font, small_font):
        overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        overlay.fill(settings.MENU_BACKGROUND)
        screen.blit(overlay, (0, 0))
        title = font.render("Seaborn: Explore and collect", True, settings.BASE_COLOR)
        screen.blit(title, (settings.SCREEN_WIDTH // 2 - title.get_width() // 2, 140))
        start = small_font.render(
            "Нажмите любую клавишу чтобы начать.", True, (200, 200, 200)
        )
        screen.blit(start, (settings.SCREEN_WIDTH // 2 - start.get_width() // 2, 220))

    def _draw_pause_overlay(self, screen, font, small_font):
        overlay = pygame.Surface(
            (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA
        )
        overlay.fill(settings.PAUSE_OVERLAY)
        screen.blit(overlay, (0, 0))
        paused_text = font.render("Пауза", True, settings.BASE_COLOR)
        resume_text = small_font.render(
            "Нажмите ESC чтобы продолжить", True, (200, 200, 200)
        )
        screen.blit(
            paused_text,
            (
                settings.SCREEN_WIDTH // 2 - paused_text.get_width() // 2,
                settings.SCREEN_HEIGHT // 2 - 20,
            ),
        )
        screen.blit(
            resume_text,
            (
                settings.SCREEN_WIDTH // 2 - resume_text.get_width() // 2,
                settings.SCREEN_HEIGHT // 2 + 20,
            ),
        )

    def _draw_end_screen(self, screen, font, small_font):
        overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        overlay.fill(settings.MENU_BACKGROUND)
        screen.blit(overlay, (0, 0))
        if self.world.player and self.world.player.oxygen <= 0:
            line = "Out of oxygen!"
        else:
            line = "Супер! Попробовать еще раз?"
        end_text = font.render(line, True, settings.BASE_COLOR)
        action_text = small_font.render(
            "Нажмите R чтобы регенерировать или ESC чтобы  остановить",
            True,
            (200, 200, 200),
        )
        screen.blit(
            end_text, (settings.SCREEN_WIDTH // 2 - end_text.get_width() // 2, 220)
        )
        screen.blit(
            action_text, (settings.SCREEN_WIDTH // 2 - action_text.get_width() // 2, 280)
        )

        if self.world.player:
            oxygen_color = (
                settings.BASE_COLOR if self.world.player.oxygen > 30 else (255, 100, 0)
            )
            oxygen_text = font.render(
                f"Кислород: {int(self.world.player.oxygen)}", True, oxygen_color
            )
            screen.blit(oxygen_text, (10, 10))

            y_pos = 50
            if hasattr(self.world.player, "inventory") and self.world.player.inventory:
                inv_header = small_font.render(
                    f"Собранные предметы: ({len(self.world.player.inventory)}):",
                    True,
                    settings.BASE_COLOR,
                )
                screen.blit(inv_header, (10, y_pos))
                y_pos = self._draw_collected_items(
                    screen, self.world.player, small_font, 10, y_pos + 25
                )

        hints = ["R - Рестарт", "ESC - Пауза"]
        for i, hint in enumerate(hints):
            text = small_font.render(hint, True, (200, 200, 200))
            screen.blit(text, (settings.SCREEN_WIDTH - 220, 10 + i * 20))
