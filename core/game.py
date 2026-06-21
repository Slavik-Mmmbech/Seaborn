"""
Модуль главного игрового контроллера Seaborn.
Обеспечивает управление игровым циклом, обработку системных событий Pygame
и координацию состояний между игровым миром и экранами пользовательского интерфейса.
"""

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
from ui.screens.menu_screen import MenuScreen
from ui.screens.pause_screen import PauseScreen
from ui.screens.end_screen import EndScreen
from ui.hud import HUD

class Game:
    """
    Основной класс игры, реализующий паттерн State (Состояние) для экранов UI
    и управляющий центральным игровым циклом (Main Loop).
    """

    def __init__(self):
        """Инициализация подсистем Pygame, аудио-менеджера, состояния мира и UI."""
        pygame.init()
        self.screen = pygame.display.set_mode(
            (display.SCREEN_WIDTH, display.SCREEN_HEIGHT)
        )
        pygame.display.set_caption(display.GAME_CAPTION)
        self.clock = pygame.time.Clock()
        
        # Инфраструктура и менеджеры данных
        self.audio_manager = AudioManager()
        self.world = World(audio_manager=self.audio_manager)
        self.world_renderer = WorldRenderer()
        self.hud = HUD(self.screen)
        
        # Загрузка графических ресурсов
        self.background = pygame.image.load(display.PATH_TO_BG_ASSET).convert()

        # Флаги состояний конечного автомата игры
        self.paused = False
        self.show_menu = True
        self.show_end_screen = False
        self.running = True
        
        # Прогресс сессии
        self.levels_completed = 0
        
        # Инициализация стартового игрового экрана
        self.world.generate()
        self.current_screen = self._create_menu_screen()

        # Запуск фонового музыкального сопровождения
        self.audio_manager.play_bgm(SoundKeys.BGM_THEME)

    def _create_menu_screen(self) -> MenuScreen:
        """Фабричный метод создания экрана главного меню."""
        return MenuScreen(self.screen)
    
    def _create_pause_screen(self) -> PauseScreen:
        """Фабричный метод создания экрана паузы с динамическим подсчетом очков."""
        screen = PauseScreen(self.screen, self.audio_manager)
        screen._calculate_score = lambda: sum(
            item.value for item in self.world.full_collection
        )
        return screen

    def _create_end_screen(self, is_victory: bool) -> EndScreen:
        """Фабричный метод создания финального экрана (Победа / Поражение)."""
        return EndScreen(self.screen, self.world.full_collection, is_victory)

    def _reset_game(self):
        """Полный сброс прогресса сессии для начала новой игры с первого уровня."""
        self.levels_completed = 0
        self.world.full_collection = []
        self.world.generate()
        self.audio_manager.play_bgm(SoundKeys.BGM_THEME)
        self.current_screen = self._create_menu_screen()

    def run(self):
        """Запуск бесконечного цикла выполнения игры (обработка -> обновление -> рендер)."""
        while self.running:
            self.clock.tick(display.FPS)
            self._handle_events()
            self._update()
            self._render()

        pygame.quit()

    def _handle_events(self) -> None:
        """Опрос и диспетчеризация системных событий Pygame."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue

            # Делегирование обработки событий активному UI-экрану
            if self.current_screen:
                command = self.current_screen.handle_event(event)
                if command:
                    self._process_screen_command(command)
                    continue

            # Обработка нажатий клавиш в режиме активного геймплея
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.current_screen = self._create_pause_screen()
                    self.audio_manager.pause_bgm()
                    continue
                if event.key == pygame.K_r:
                    self._handle_r_key()
                elif event.key == pygame.K_SPACE and self.world.active_storyteller:
                    # Сброс окна диалога с NPC
                    self.world.active_storyteller = None
                    self.world.talk_text = ""
                elif event.key == pygame.K_e:
                    self._handle_interaction()

    def _process_screen_command(self, command: str) -> None:
        """Интерпретация строковых команд, возвращаемых экранами UI."""
        if command == "quit":
            self.running = False
        elif command == "start_game":
            self.world.generate()
            self.current_screen = None  # Снятие экрана переключает фокус на рендер мира
        elif command == "resume":
            self.audio_manager.unpause_bgm()
            self.current_screen = None
        elif command == "restart":
            self._reset_game()

    def _handle_r_key(self) -> None:
        """Логика клавиши перезапуска/перехода. Действие зависит от контекста мира."""
        if self.world.player and self.world.player.oxygen <= 0:
            self.current_screen = self._create_end_screen(is_victory=False)
        elif self.world.player_in_exit_zone:
            self._complete_level()
        else:
            self.world.generate()

    def _handle_interaction(self) -> None:
        """Попытка взаимодействия с окружающими интерактивными объектами (NPC)."""
        if self.world.active_storyteller:
            self.world.active_storyteller = None
            self.world.talk_text = ""
            return
        
        storyteller = self.world.npc_manager.get_nearby_storyteller(self.world.player)
        if storyteller:
            self.audio_manager.play_sfx(SoundKeys.TALK)
            self.world.active_storyteller = storyteller
            lore_text, reward = storyteller.talk()
            if reward:
                self._apply_storyteller_reward(reward, lore_text)
    
    def _apply_storyteller_reward(self, reward: str, lore_text: str) -> None:
        """Применение эффектов наград, полученных в ходе беседы со Сказителем."""
        if reward == "oxygen_bonus" and self.world.player:
            self.world.player.oxygen = min(
                self.world.player.oxygen + gameplay.STORYTELLER_OXYGEN_BONUS, 
                gameplay.PLAYER_MAX_OXYGEN
            )
            self.world.talk_text = f"{lore_text} [ДРЕВНИЙ ДУХ ДАРУЕТ ВОЗДУХ! +{gameplay.STORYTELLER_OXYGEN_BONUS} O₂]"
        elif reward == "rare_lore":
            success = self._give_random_item(Rarity.LEGENDARY, "Реликвия")
            msg = " [ЛЕГЕНДАРНЫЙ РЕЛИКТ ПОЛУЧЕН!]" if success else " [ИНВЕНТАРЬ ПОЛОН!]"
            self.world.talk_text = f"{lore_text}\n\n{msg}"
        elif reward == "hint":
            success = self._give_random_item(Rarity.EPIC, "Артефакт")
            msg = " [ЭПИЧЕСКИЙ АРТЕФАКТ ПОЛУЧЕН!]" if success else " [ИНВЕНТАРЬ ПОЛОН!]"
            self.world.talk_text = f"{lore_text}\n\n{msg}"
        else:
            self.world.talk_text = lore_text

    def _complete_level(self) -> None:
        """Фиксация результатов завершения текущего уровня и перенос лута в общую коллекцию."""
        if self.world.player and self.world.player.inventory:
            score = self.world.player.calculate_score()
            items_count = len(self.world.player.inventory)
            print(f"Успешное возвращение! Score: {score}")
            print(f"Собрано предметов: {items_count}")
            self.world.full_collection.extend(self.world.player.inventory)

        self.world.level_complete = True

    def _update(self) -> None:
        """Обновление игровой логики симуляции (вызывается только вне экранов меню/паузы)."""
        if self.current_screen is not None:
            return

        self.world.update(pygame.key.get_pressed())

        # Проверка триггеров окончания игры/уровня
        if self.world.player and self.world.player.oxygen <= 0:
            self.audio_manager.play_sfx(SoundKeys.LOSE)
            self.current_screen = self._create_end_screen(is_victory=False)
        elif self.world.level_complete:
            self.levels_completed += 1
            self.world.level_complete = False
            if self.levels_completed >= gameplay.LEVEL_COUNT_TO_COMPLETE:
                self.audio_manager.play_sfx(SoundKeys.WIN)
                self.current_screen = self._create_end_screen(is_victory=True)
            else:
                self.world.generate()

    def _render(self) -> None:
        """Отрисовка кадра на экране."""
        self.screen.blit(self.background, (0, 0))

        if self.current_screen is None:
            # Рендер активной игры: игровой мир + HUD игрока
            self.world_renderer.draw_world(self.screen, self.world)
            self.hud.draw(self.world)
        else:
            # Рендер интерфейсных оверлеев/экранов
            if isinstance(self.current_screen, PauseScreen):
                score = sum(item.value for item in self.world.full_collection)
                self.current_screen.draw(score)
            else:
                self.current_screen.draw()

        pygame.display.flip()
    
    def _give_random_item(self, rarity: Rarity, item_name: str) -> bool:
        """Создает и выдает игроку случайный предмет заданной редкости на основе параметров веса."""
        if not self.world.player or not hasattr(self.world.player, "inventory"):
            return False

        cfg = gameplay.ITEM_RARITY_CONFIG.get(rarity)
        if not cfg:
            return False

        min_w, max_w, value_mult, _ = cfg
        item = Item(
            item_name, rarity,
            random.uniform(min_w, max_w),
            random.uniform(gameplay.STORYTELLER_PICKUP_MIN_VAL, gameplay.STORYTELLER_PICKUP_MAX_VAL) * value_mult,
        )
        return self.world.player.pickup(item)