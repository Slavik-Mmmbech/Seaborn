import pygame
import random

from entities.items import Item
from core.managers.audio_manager import AudioManager
from config.audio_config import SoundKeys
import config.display_config as display
import config.gameplay_config as gameplay
from core.world import World
from config.enums import Rarity
from rendering import WorldRenderer


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (display.SCREEN_WIDTH, display.SCREEN_HEIGHT)
        )
        pygame.display.set_caption("Seaborn")
        self.background = pygame.image.load(
            "assets/bg/background.jpg"
        ).convert()
        self.clock = pygame.time.Clock()
        self.world = World()
        self.audio_manager = AudioManager()
        self.world = World(audio_manager=self.audio_manager)
        self.world.generate()
        self.debug_mode = True
        self.running = True
        self.paused = False
        self.show_menu = True
        self.show_end_screen = False
        self.levels_completed = 0
        self.world_renderer = WorldRenderer()
        self.audio_manager.play_bgm(SoundKeys.BGM_THEME)

    def _reset_game(self):
        self.levels_completed = 0
        self.world.full_collection = []
        self.world.generate()
        self.audio_manager.play_bgm(SoundKeys.BGM_THEME)
        self.paused = False
        self.show_menu = False
        self.show_end_screen = False
        if not pygame.mixer.music.get_busy():
            self.audio_manager.play_bgm(SoundKeys.BGM_THEME)

    def run(self):
        while self.running:
            self.clock.tick(display.FPS)

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
                            if self.paused:
                                self.audio_manager.pause_bgm()
                            else:
                                self.audio_manager.unpause_bgm()
                    elif self.paused:
                        if event.key == pygame.K_m:
                            self.audio_manager.toggle_bgm()
                        elif event.key == pygame.K_s:
                            self.audio_manager.toggle_sfx()
                    elif event.key == pygame.K_r:
                        if self.show_menu or self.show_end_screen:
                            self._reset_game()
                        elif self.world.player and self.world.player.oxygen <= 0:
                            self._reset_game()
                        elif self.world.player_in_exit_zone:
                            if self.world.player:
                                score = self.world.player.calculate_score() if self.world.player.inventory else 0
                                items_count = len(self.world.player.inventory)
                                print(f"Успешное возвращение! Score: {score}")
                                print(f"Собрано предметов: {items_count}")
                                self.world.full_collection.extend(i for i in self.world.player.inventory)
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
                            storyteller = self.world.npc_manager.get_nearby_storyteller(self.world.player)
                            if storyteller:
                                self.audio_manager.play_sfx(SoundKeys.TALK)  
                                self.world.active_storyteller = storyteller
                                lore_text, reward = storyteller.talk()

                                if reward == "oxygen_bonus":
                                    if self.world.player:
                                        self.world.player.oxygen = min(
                                            self.world.player.oxygen + 25,
                                            gameplay.PLAYER_MAX_OXYGEN,
                                        )
                                    self.world.talk_text = f"{lore_text}  [ДРЕВНИЙ ДУХ ДАРУЕТ BОЗДУХ! +25 O₂]"
                                elif reward == "rare_lore":
                                    success = self._give_random_item(Rarity.LEGENDARY, "Реликвия")
                                    msg = " [ЛЕГЕНДАРНЫЙ РЕЛИКТ ПОЛУЧЕН!]" if success else " [ИНВЕНТАРЬ ПОЛОН!]"
                                    self.world.talk_text = (
                                        f"{lore_text}\n\n{msg}"
                                    )
                                elif reward == "hint":
                                    success = self._give_random_item(Rarity.EPIC, "Артефакт")
                                    msg = " [ЭПИЧЕСКИЙ АРТЕФАКТ ПОЛУЧЕН!]" if success else " [ИНВЕНТАРЬ ПОЛОН!]"
                                    self.world.talk_text = (
                                        f"{lore_text}\n\n{msg}"
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
                    self.audio_manager.play_sfx(SoundKeys.LOSE)
                if self.world.level_complete:
                    self.levels_completed += 1
                    self.world.level_complete = False
                    if self.levels_completed >= gameplay.LEVEL_COUNT_TO_COMPLETE:
                        self.show_end_screen = True
                        self.audio_manager.play_sfx(SoundKeys.WIN)
                    else:
                        self.world.generate()

            self.screen.blit(self.background, (0, 0))
            if not self.show_menu:
                self.world_renderer.draw_world(self.screen, self.world)

            self.draw_ui(self.screen)
            pygame.display.flip()

        pygame.quit()

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
            oxygen_color = display.BASE_COLOR if oxygen > gameplay.OXYGEN_CRITICAL_THRESHOLD else (255, 100, 0)
            oxygen_text = font.render(f"Кислород: {int(oxygen)}", True, oxygen_color)
            screen.blit(oxygen_text, (10, 10))

            if hasattr(self.world.player, "inventory"):
                inv_count_text = small_font.render(
                    f"Предметы: {len(self.world.player.inventory)} (Общий вес: {self.world.player.inventory.current_weight:.1f}/{self.world.player.inventory.max_weight})",
                    True,
                    display.BASE_COLOR,
                )
                screen.blit(inv_count_text, (10, 50))

                y_offset = 70

                for item in self.world.player.inventory:
                    rarity_color = display.RARITY_COLORS.get(
                        item.rarity, display.BASE_COLOR
                    )
                    item_text = small_font.render(
                        f"• {item.name} ({item.rarity.value})", True, rarity_color
                    )
                    screen.blit(item_text, (10, y_offset))
                    y_offset += 22

                    if y_offset > display.SCREEN_HEIGHT // 2:
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
                center=(display.SCREEN_WIDTH // 2, display.SCREEN_HEIGHT // 2 - 100)
            )
            screen.blit(notification_text, notification_rect)

        if self.world.player_in_exit_zone:
            exit_prompt_font = pygame.font.Font(None, 28)
            exit_text = exit_prompt_font.render(
                "Нажмите R: Завершить уровень?", True, (100, 255, 100)
            )
            exit_rect = exit_text.get_rect(
                center=(display.SCREEN_WIDTH // 2, display.SCREEN_HEIGHT - 100)
            )
            pygame.draw.rect(screen, (50, 100, 50), exit_rect.inflate(20, 10))
            pygame.draw.rect(screen, (100, 255, 100), exit_rect.inflate(20, 10), 2)
            screen.blit(exit_text, exit_rect)

        hints = [
            "WASD/Arrows - Движение",
            "E - Говорить с storyteller",
            "R - Регенерировать",
            "ESC - Пауза",
        ]
        for i, hint in enumerate(hints):
            text = small_font.render(hint, True, (200, 200, 200))
            screen.blit(text, (display.SCREEN_WIDTH - 220, 10 + i * 20))

        if self.world.active_storyteller and self.world.talk_text:
            talk_box = pygame.Rect(
                70, display.SCREEN_HEIGHT - 160, display.SCREEN_WIDTH - 140, 120
            )
            pygame.draw.rect(screen, (0, 0, 0), talk_box)
            pygame.draw.rect(screen, display.BASE_COLOR, talk_box, 2)
            rendered = small_font.render(
                "Нажмите SPACE или E чтобы закрыть", True, display.BASE_COLOR
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
                "Нажмите E чтобы говорить с storyteller", True, display.BASE_COLOR
            )
            screen.blit(
                prompt,
                (
                    display.SCREEN_WIDTH // 2 - prompt.get_width() // 2,
                    display.SCREEN_HEIGHT - 60,
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
        overlay = pygame.Surface((display.SCREEN_WIDTH, display.SCREEN_HEIGHT))
        overlay.fill(display.MENU_BACKGROUND)
        screen.blit(overlay, (0, 0))
        title = font.render("Seaborn: Explore and collect", True, display.BASE_COLOR)
        screen.blit(title, (display.SCREEN_WIDTH // 2 - title.get_width() // 2, 140))
        start = small_font.render(
            "Нажмите любую клавишу чтобы начать.", True, (200, 200, 200)
        )
        screen.blit(start, (display.SCREEN_WIDTH // 2 - start.get_width() // 2, 220))

    def _give_random_item(self, rarity: Rarity, item_name: str) -> bool:
        """
        Создает и выдает игроку случайный предмет заданной редкости.
        Возвращает True, если предмет успешно добавлен в инвентарь.
        """
        if not self.world.player or not hasattr(self.world.player, "inventory"):
            return False
            
        cfg = gameplay.ITEM_RARITY_CONFIG.get(rarity)
        if not cfg:
            return False
            
        min_w, max_w, value_mult, _ = cfg
        item = Item(
            item_name,
            rarity, 
            random.uniform(min_w, max_w), 
            random.uniform(10.0, 25.0) * value_mult
        )
        
        return self.world.player.pickup(item)
    
    def _draw_pause_overlay(self, screen, font, small_font):
        overlay = pygame.Surface(
            (display.SCREEN_WIDTH, display.SCREEN_HEIGHT), pygame.SRCALPHA
        )
        overlay.fill(display.PAUSE_OVERLAY)
        screen.blit(overlay, (0, 0))
        paused_text = font.render("Пауза", True, display.BASE_COLOR)
        resume_text = small_font.render(
            "Нажмите ESC чтобы продолжить", True, (200, 200, 200)
        )
        current_score= sum(item.value for item in self.world.full_collection)

        score_text = font.render(
            f"Нынешний счет: {int(current_score)}",
            True, display.BASE_COLOR
            )

        center_x = display.SCREEN_WIDTH // 2
        current_y = 200

        screen.blit(score_text, (center_x - score_text.get_width() // 2, current_y))
        screen.blit(
            paused_text,
            (
                display.SCREEN_WIDTH // 2 - paused_text.get_width() // 2,
                display.SCREEN_HEIGHT // 2 - 20,
            ),
        )
        screen.blit(
            resume_text,
            (
                display.SCREEN_WIDTH // 2 - resume_text.get_width() // 2,
                display.SCREEN_HEIGHT // 2 + 20,
            ),
        )
        sfx_status = "ВКЛ" if self.audio_manager.sfx_enabled else "ВЫКЛ"
        bgm_status = "ВКЛ" if self.audio_manager.bgm_enabled else "ВЫКЛ"
        
        audio_info = small_font.render(
            f"[M] Музыка: {bgm_status}    [S] Звуки: {sfx_status}",
            True, display.GREY
        )
        screen.blit(
            audio_info,
            (center_x - audio_info.get_width() // 2, current_y + 220)
        )

    def _draw_end_screen(self, screen, font, small_font):
        overlay = pygame.Surface((display.SCREEN_WIDTH, display.SCREEN_HEIGHT))

        total_score = sum(item.value for item in self.world.full_collection)
        
        if self.world.player and self.world.player.oxygen <= 0:
            overlay.fill(display.LOSE_BACKGROUND)
            line = "Кислород закончился!"
            title_color = display.END_OF_OXYGEN_LINE_COLOR
        else:
            overlay.fill(display.WIN_BACKGROUND)
            line = "Уровень завершен!"
            title_color = display.END_OF_LEVEL_LINE_COLOR

        screen.blit(overlay, display.BASE_COORDS)
        big_font = pygame.font.Font(None, 56)
        end_text = big_font.render(line, True, title_color)
        score_text = font.render(f"Общий счет: {int(total_score)}", True, display.GOLD)
        items_header = font.render(
            f"Собранные предметы ({len(self.world.full_collection)}):", 
            True, 
            display.BASE_COLOR
            )
        
        center_x = display.SCREEN_WIDTH // 2
        current_y = 120
        
        screen.blit(end_text, (center_x - end_text.get_width() // 2, current_y))
        current_y += 70
        
        screen.blit(score_text, (center_x - score_text.get_width() // 2, current_y))
        current_y += 50
        
        screen.blit(items_header, (center_x - items_header.get_width() // 2, current_y))
        current_y += 40
        
        if self.world.audio:
            self.world.audio.stop_bgm()
        max_items_to_show = display.OVERFLOW_PROTECTION
        items_to_show = self.world.full_collection[:max_items_to_show]
        
        for item in items_to_show:
            rarity_color = display.RARITY_COLORS.get(item.rarity, display.BASE_COLOR)
            # Формат: Rarity - Value
            item_str = f"• {item.name} ({item.rarity.value}) - {int(item.value)}"
            item_text = small_font.render(item_str, True, rarity_color)
            screen.blit(item_text, (center_x - item_text.get_width() // 2, current_y))
            current_y += 25
            
        if len(self.world.full_collection) > max_items_to_show:
            remaining = len(self.world.full_collection) - max_items_to_show
            more_text = small_font.render(f"... и еще {remaining} предметов", 
                                          True, 
                                          display.MORE_ITEMS_COLOR)
            screen.blit(more_text, (center_x - more_text.get_width() // 2, current_y))
            current_y += 30

        current_y += 30
        hint = font.render("Нажмите R для новой игры", True, display.GREY)
        screen.blit(hint, (center_x - hint.get_width() // 2, current_y))