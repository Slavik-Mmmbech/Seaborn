# core/world.py
import pygame
import random
from typing import List
from entities.player import Player
from entities.collectible import Collectible
from entities.items import Item
from loot.loot_bag import LootBag
from generation.dungeon import DungeonGenerator
import config

# Слабая имплементация модулей, интегрирование алгоритмов в
# игровой процесс в будущем.
class World:
    """Состояние игрового уровня: коллизии, сущности, геометрия подземелья."""
    
    def __init__(self):
        self.player: Player | None = None
        self.collectibles: List[Collectible] = []
        self.rooms: List[pygame.Rect] = []
        self.corridors: List[tuple] = []
        self.walkable_areas: List[pygame.Rect] = []
        self.walls: List[pygame.Rect] = []
        self.room_values = {}
        self.collected_items = []
        self.entry_point = None  # Где начал игрок
        self.exit_rect = None  # Зона выхода
        self.is_returning = False 

    def _assign_room_values(self) -> None:
        """Назначает ценность комнатам: дальше от входа = ценнее"""
        if not self.rooms or not self.entry_point:
            return
            
        max_dist = 0
        for i, room in enumerate(self.rooms):
            dist = self._calculate_distance(self.entry_point, room.center)
            max_dist = max(max_dist, dist)
        
        # Нормализуем ценность (0.0-1.0)
        for i, room in enumerate(self.rooms):
            dist = self._calculate_distance(self.entry_point, room.center)
            self.room_values[i] = dist / max_dist if max_dist > 0 else 0
    
    def _calculate_distance(self, point1, point2) -> float:
        """Расстояние между двумя точками"""
        return ((point1[0] - point2[0])**2 + 
                (point1[1] - point2[1])**2)**0.5
    

    def generate(self) -> None:
        """Инициализирует уровень: вызывает генератор, размещает игрока и лут."""
        # 1. Генерация геометрии
        dg = DungeonGenerator(config.SCREEN_WIDTH, config.SCREEN_HEIGHT, depth=4)
        self.rooms, self.corridors = dg.generate()

        self._build_walkable_areas()
        print(f"Walkable areas: {len(self.walkable_areas)}")
        self._generate_walls_from_geometry()

        # 3. Спавн игрока в первой комнате
        if self.rooms:
            start_room = self.rooms[0]
            self.player = Player(start_room.centerx, start_room.centery)

        if self.rooms:
            self.entry_point = self.rooms[0].center
            self.exit_rect = self.rooms[0].copy()
            self.exit_rect.inflate_ip(-20, -20)

        # 4. Спавн лута внутри комнат
        self._spawn_collectibles()

    def _build_walkable_areas(self) -> None:
        """Создает список всех проходимых зон (комнаты + коридоры)"""
        self.walkable_areas = []
        
        # Добавление комнат
        for room in self.rooms:
            self.walkable_areas.append(room.copy())
        
        # Преобразование коридоров в прямоугольники
        for corridor in self.corridors:
            x1, y1, x2, y2 = corridor
            # Создание прямоугольника коридора с толщиной 12 пикселей
            corridor_rect = pygame.Rect(
                min(x1, x2) - 6,
                min(y1, y2) - 6,
                abs(x2 - x1) + 12,
                abs(y2 - y1) + 12
            )
            self.walkable_areas.append(corridor_rect)

    def _generate_walls_from_walkable_areas(self) -> None:
        """Создает стены как границы проходимых зон + границы экрана"""
        self.walls = []
        
        # 1. Границы экрана
        border_thickness = 4
        screen_borders = [
            pygame.Rect(0, 0, config.SCREEN_WIDTH, border_thickness),
            pygame.Rect(0, config.SCREEN_HEIGHT - border_thickness, config.SCREEN_WIDTH, border_thickness),
            pygame.Rect(0, 0, border_thickness, config.SCREEN_HEIGHT),
            pygame.Rect(config.SCREEN_WIDTH - border_thickness, 0, border_thickness, config.SCREEN_HEIGHT),
        ]
        self.walls.extend(screen_borders)

    def _is_position_valid(self, rect: pygame.Rect) -> bool:
        """Проверяет, находится ли центр игрока в проходимой зоне"""
        if not self.walkable_areas:
            return False
            
        # Создаем маленькую точку в центре игрока для проверки
        center_x = rect.centerx
        center_y = rect.centery
        point_rect = pygame.Rect(center_x - 2, center_y - 2, 4, 4)
        
        for area in self.walkable_areas:
            if point_rect.colliderect(area):
                return True
        return False
    
    def _spawn_collectibles(self) -> None:
        """Размещает предметы строго внутри границ комнат с безопасным отступом."""
        if not self.rooms:
            return
            
        bag = LootBag()

        for _ in range(10):
            rarity = bag.draw()
            item = Item("loot", rarity, 7, 25)
            
            room = random.choice(self.rooms)
            # Безопасная зона внутри комнаты (отступ 20px от стен)
            safe_x = random.randint(room.left + 20, room.right - 20)
            safe_y = random.randint(room.top + 20, room.bottom - 20)
            
            self.collectibles.append(Collectible(safe_x, safe_y, item))
    
    def draw_debug(self, screen: pygame.Surface) -> None:
        """Отрисовка BSP структуры для отладки"""
        debug_surface = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        debug_surface.set_alpha(50)
        debug_surface.fill((0, 255, 0))
        
        for area in self.walkable_areas:
            pygame.draw.rect(debug_surface, (0, 255, 0), area)
    
        screen.blit(debug_surface, (0, 0))
        for i, room in enumerate(self.rooms):
            color = (100 + (i * 30) % 100, 150 + (i * 20) % 50, 100)
            pygame.draw.rect(screen, color, room)
            pygame.draw.rect(screen, (255, 255, 255), room, width=1)
            
            # Нумерация комнат
            font = pygame.font.Font(None, 24)
            text = font.render(str(i), True, (255, 255, 255))
            screen.blit(text, (room.centerx - 10, room.centery - 10))
        
        # Отрисовка коридоров
        for corridor in self.corridors:
            x1, y1, x2, y2 = corridor
            pygame.draw.line(screen, (255, 200, 0), (x1, y1), (x2, y2), width=4)
            
            # Точки соединения
            pygame.draw.circle(screen, (255, 100, 0), (x1, y1), 3)
            pygame.draw.circle(screen, (255, 100, 0), (x2, y2), 3)
        
        # Инфо о генерации
        font = pygame.font.Font(None, 28)
        info = [
            f"Rooms: {len(self.rooms)}",
            f"Corridors: {len(self.corridors)}",
            f"Press R - Regenerate",
            f"Press D - Toggle Debug"
        ]
        
        for i, text in enumerate(info):
            rendered = font.render(text, True, (255, 255, 255))
            screen.blit(rendered, (10, 10 + i * 30))

    def _generate_walls_from_geometry(self) -> None:
        """
        Создаёт стены как границы между проходимыми зонами и водой.
        Упрощённая версия: стены только по периметру экрана + границы комнат.
        """
        self.walls = []
        
        # 1. Границы экрана (внешние стены)
        border_thickness = 4
        self.walls.extend([
            pygame.Rect(0, 0, config.SCREEN_WIDTH, border_thickness),
            pygame.Rect(0, config.SCREEN_HEIGHT - border_thickness, config.SCREEN_WIDTH, border_thickness),
            pygame.Rect(0, 0, border_thickness, config.SCREEN_HEIGHT),
            pygame.Rect(config.SCREEN_WIDTH - border_thickness, 0, border_thickness, config.SCREEN_HEIGHT),
        ])

    def update(self, keys: dict) -> None:
        if self.player:
            if self.exit_rect and self.player.rect.colliderect(self.exit_rect):
                if hasattr(self.player, 'inventory') and self.player.inventory:
                    score = self.player.calculate_score()
                    print(f"Успешное возвращение! Score: {score}")
                    print(f"Собрано предметов: {len(self.player.inventory)}")
                    self.generate()  # Новый уровень
                    return
            
            old_x = self.player.x
            old_y = self.player.y
            
            self.player.handle_input(keys, [])

            if not self._is_position_valid(self.player.rect):
                self.player.x = old_x
                self.player.y = old_y
                self.player.rect.x = old_x
                self.player.rect.y = old_y
            
            self.player.oxygen -= config.OXYGEN_DRAIN_PER_SECOND / config.FPS
            
            if self.player.oxygen <= 0:
                print("GAME OVER - Out of oxygen!")

        if self.player:
            for c in self.collectibles[:]:
                if c.try_collect(self.player.rect):
                    print(f"Collected: {c.item}")
                    
                    if hasattr(self.player, 'pickup'):
                        if self.player.pickup(c.item):
                            self.collectibles.remove(c)
                            self.player.oxygen = min(
                                self.player.oxygen + 10, 
                                config.PLAYER_MAX_OXYGEN
                            )

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill(config.WATER_COLOR)

        floor_color = (60, 80, 110)
        for room in self.rooms:
            pygame.draw.rect(screen, floor_color, room)

        corridor_color = (100, 130, 160)
        for x1, y1, x2, y2 in self.corridors:
            pygame.draw.line(screen, corridor_color, (x1, y1), (x2, y2), width=8)
        
        wall_color = (20, 30, 45)
        for room in self.rooms:
            pygame.draw.rect(screen, wall_color, room, width=1)

        if self.player:
            pygame.draw.rect(screen, (0, 200, 255), self.player.rect)
        
        for c in self.collectibles:
            pygame.draw.rect(screen, (255, 200, 0), c.rect)
        
        if self.exit_rect:
            pygame.draw.rect(screen, (0, 255, 100), self.exit_rect, width=2)