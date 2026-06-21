# core/world.py
import math
import pygame
import random
from typing import Any, List, Sequence, Tuple

import ai
import config.content_config as content
from config.enums import TileType
import config.display_config as display
import config.gameplay_config as gameplay
import config.generation_config as gen
from config.logging_config import setup_logger
from core.managers.collision_manager import CollisionManager
from core.managers.npc_manager import NPCManager
from core.managers.items_manager import CollectibleSpawnManager
from entities.items import Collectible
from entities.items import Item
from entities.npc import NPC, NPCType
from entities.player import Player
from generation.dungeon import DungeonGenerator
from lighting.lightmap_raycasting import Raycaster
from loot.loot_bag import LootBag
from loot.weighted_binary import WeightedBinaryLootGenerator
from spatial.quadtree import QuadTree, Bounds

logger = setup_logger(__name__)


class World:
    """Состояние игрового уровня: коллизии, сущности, геометрия подземелья."""

    def __init__(self, audio_manager=None):
        self.player: Player | None = None
        self.collectibles: List[Collectible] = []
        self.rooms: Sequence[Any] = []
        self.corridors: List[tuple] = []
        self.walkable_areas: List[pygame.Rect] = []
        self.walls: List[pygame.Rect] = []
        self.room_values = {}
        self.collected_items = []
        self.full_collection = []
        self.npcs: List[NPC] = []
        self.entry_point = None  # Где начал игрок
        self.exit_rect = None  # Зона выхода
        self.is_returning = False
        self.light_grid: List[List[int]] = []
        self.raycaster: Raycaster | None = None
        self.level_index = 0
        self.completed_levels = 0
        self.audio = audio_manager
        self.story_mode_active = False
        self.active_storyteller: NPC | None = None
        self.talk_text = ""
        self.notification_message = ""
        self.notification_time = 0.0
        self.player_in_exit_zone = False
        world_bounds = Bounds(0, 0, display.SCREEN_WIDTH, display.SCREEN_HEIGHT)
        self.spatial_index = QuadTree(
            world_bounds, max_capacity=gen.MAX_CAPACITY, max_depth=gen.MAX_DEPTH
        )
        self.level_complete = False
        self.walkable_areas = []
        self.collectibles = []
        self.npcs = []

        self.collision_manager = CollisionManager(walkable_areas=[]) 
        self.items_manager = None
        self.npc_manager = NPCManager(entry_point=(0,0), audio_manager=audio_manager)


    def _room_to_rect(self, room_data: Tuple[int, int, int, int]) -> pygame.Rect:
        """Преобразует кортеж комнаты в pygame.Rect."""
        return pygame.Rect(*room_data)

    def _get_room_center(self, room_data: Tuple[int, int, int, int]) -> Tuple[int, int]:
        """Возвращает центр комнаты из кортежа."""
        x, y, width, height = room_data
        return (x + width // 2, y + height // 2)

    def _assign_room_values(self) -> None:
        """Назначает ценность комнатам: дальше от входа = ценнее"""
        if not self.rooms or not self.entry_point:
            return

        max_dist = 0
        for room_data in self.rooms:
            center = self._get_room_center(room_data)
            dist = self._calculate_distance(self.entry_point, center)
            max_dist = max(max_dist, dist)

        for i, room_data in enumerate(self.rooms):
            center = self._get_room_center(room_data)
            dist = self._calculate_distance(self.entry_point, center)
            self.room_values[i] = dist / max_dist if max_dist > 0 else 0

    def _calculate_distance(self, point1, point2) -> float:
        """Расстояние между двумя точками"""
        return ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5

    def generate(self) -> None:
        """
        Инициализирует уровень: вызывает генератор,
        размещает игрока и лут.
        """
        self.rooms = []
        self.corridors = []
        self.walkable_areas = []
        self.walls = []
        self.room_values = {}
        self.collectibles = []
        self.npcs = []
        self.collected_items = []
        self.entry_point = None
        self.exit_rect = None
        self.is_returning = False
        self.light_grid = []
        self.raycaster = None
        self.notification_message = ""
        self.notification_time = 0.0
        self.player_in_exit_zone = False
        self.spatial_index.clear()

        dg = DungeonGenerator(
            display.SCREEN_WIDTH, display.SCREEN_HEIGHT, depth=gen.DEFAULT_BSP_DEPTH
        )
        self.rooms, self.corridors = dg.generate()

        # Построение геометрии
        self._build_walkable_areas()
        self.collision_manager.walkable_areas = self.walkable_areas
        self._generate_walls_from_geometry()
        self._build_light_grid()

        # Спавн сущностей
        if self.rooms:
            start_room = pygame.Rect(*self.rooms[0])
            self.player = Player(start_room.centerx, start_room.centery)
            self.entry_point = start_room.center
            self.exit_rect = start_room.copy()
            self.exit_rect.inflate_ip(gameplay.NPC_COORD, gameplay.NPC_COORD)

        self._assign_room_values()
        self.items_manager = CollectibleSpawnManager(
            rooms=self.rooms,
            room_values=self.room_values
        )
        self.collectibles = self.items_manager.spawn_collectibles()
        self._update_spatial_index()
        self.npc_manager = NPCManager(
            entry_point=self.entry_point,
            audio_manager=self.audio
        )
        self.npc_manager.spawn_all_npcs(
            rooms=[pygame.Rect(*room_data) for room_data in self.rooms],
            build_lore_chain_func=self._build_lore_chain,
            create_behavior_tree_func=self._create_npc_behavior_tree_from_factory
        )
        self.npcs = self.npc_manager.npcs
        self.level_complete = False
        logger.debug(f"Сгенерированы NPC: {self.npcs}")

    def _create_npc_behavior_tree_from_factory(self, npc: NPC) -> ai.BTNode:
        """Создаёт дерево поведения через фабрику."""
        from ai.behavior_tree_factory import NPCBehaviorTreeFactory
        factory = NPCBehaviorTreeFactory()
        return factory.create_behavior_tree(npc)

    def _build_walkable_areas(self) -> None:
        """Создает список всех проходимых зон (комнаты + коридоры)"""
        self.walkable_areas = []

        # Добавление комнат.
        for room_data in self.rooms:
            self.walkable_areas.append(pygame.Rect(*room_data))

        # Коридоры
        corridor_width = display.CORRIDOR_WIDTH
        half_width = corridor_width // 2

        for corridor in self.corridors:
            x1, y1, x2, y2 = corridor

            if x1 == x2:  # Вертикальный
                corridor_rect = pygame.Rect(
                    x1 - half_width, min(y1, y2), corridor_width, abs(y2 - y1)
                )
            else:  # Горизонтальный
                corridor_rect = pygame.Rect(
                    min(x1, x2), y1 - half_width, abs(x2 - x1), corridor_width
                )

            self.walkable_areas.append(corridor_rect)

    def _update_spatial_index(self) -> None:
        """
        Обновляет пространственный индекс для динамических объектов.
        Вызывается при спавне новых предметов или после их сбора.
        """
        self.spatial_index.clear()

        for collectible in self.collectibles:
            # Преобразование pygame.Rect в Bounds для QuadTree
            item_bounds = Bounds(
                collectible.rect.x,
                collectible.rect.y,
                collectible.rect.width,
                collectible.rect.height,
            )
            self.spatial_index.insert(collectible, item_bounds)

    def _generate_walls_from_geometry(self) -> None:
        """
        Создаёт стены как границы между проходимыми зонами и водой.
        """
        self.walls = []

        # 1. Границы экрана (внешние стены)
        self.walls.extend(
            [
                pygame.Rect(0, 0, display.SCREEN_WIDTH, display.WALL_THICKNESS),
                pygame.Rect(
                    0,
                    display.SCREEN_HEIGHT -  gameplay.VALID_DELTA,
                    display.SCREEN_WIDTH,
                     gameplay.VALID_DELTA,
                ),
                pygame.Rect(0, 0,  gameplay.VALID_DELTA, display.SCREEN_HEIGHT),
                pygame.Rect(
                    display.SCREEN_WIDTH -  gameplay.VALID_DELTA,
                    0,
                     gameplay.VALID_DELTA,
                    display.SCREEN_HEIGHT,
                ),
            ]
        )

    def _build_light_grid(self) -> None:
        """Строит сетку препятствий для светового рендеринга."""
        grid_width = display.SCREEN_WIDTH // display.TILE_SIZE
        grid_height = display.SCREEN_HEIGHT // display.TILE_SIZE

        self.light_grid = [[0] * grid_width for _ in range(grid_height)]

        for gy in range(grid_height):
            for gx in range(grid_width):
                cell_center = (
                    gx * display.TILE_SIZE + display.TILE_SIZE / 2,
                    gy * display.TILE_SIZE + display.TILE_SIZE / 2,
                )

                if not any(
                    area.collidepoint(cell_center) for area in self.walkable_areas
                ):
                    self.light_grid[gy][gx] = gameplay.EMPTY

        for gy in range(grid_height):
            for gx in range(grid_width):
                if self.light_grid[gy][gx] == gameplay.EMPTY:
                    is_border_wall = False
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            ny, nx = gy + dy, gx + dx
                            if 0 <= nx < grid_width and 0 <= ny < grid_height:
                                if self.light_grid[ny][nx] == 0:
                                    is_border_wall = True
                                    break
                        if is_border_wall:
                            break

                    if is_border_wall:
                        self.light_grid[gy][gx] = TileType.WALL
                    else:
                        self.light_grid[gy][gx] = 0

        self.raycaster = Raycaster(self.light_grid, display.TILE_SIZE)

    def _build_lore_chain(self) -> ai.MarkovChain:
        transitions = content.GAME_TRANSITIONS
        return ai.MarkovChain(transitions)

    def update(self, keys: Any) -> None:
        if not self.player:
            return

        # Update notification timer
        if self.notification_time > 0:
            self.notification_time -= 1 / display.FPS
        else:
            self.notification_message = ""

        # Check if player is in exit zone
        self.player_in_exit_zone = False
        if self.exit_rect and self.player.rect.colliderect(self.exit_rect):
            self.player_in_exit_zone = True

        old_x = self.player.x
        old_y = self.player.y

        self.player.handle_input(keys)

        if not self.collision_manager.is_position_valid(self.player.rect):
            self.player.x = old_x
            self.player.y = old_y
            self.player.rect.x = int(old_x)
            self.player.rect.y = int(old_y)

        self.player.oxygen -= gameplay.OXYGEN_DRAIN_PER_SECOND / display.FPS

        for npc in self.npcs:
            self.player.oxygen -= npc.apply_player_effect(self.player)
            if npc.npc_type == NPCType.STORYTELLER:
                distance = self._calculate_distance(
                    npc.position, self.player.rect.center
                )
                npc.blackboard.set(
                    "sees_player", distance <= gameplay.NPC_TALK_DISTANCE
                )

        if self.player.oxygen <= 0:
            print("GAME OVER - Out of oxygen!")

        player_bounds = Bounds(
            self.player.rect.x,
            self.player.rect.y,
            self.player.rect.width,
            self.player.rect.height,
        )

        nearby_collectibles = self.spatial_index.query(player_bounds)

        collected_this_frame = []

        for c in nearby_collectibles[:]:
            if c.try_collect(self.player.rect):
                print(f"Собрано: {c.item}")
                if hasattr(self.player, "pickup"):
                    if self.player.pickup(c.item):
                        if self.audio is not None:
                            from config.audio_config import SoundKeys

                            self.audio.play_sfx(SoundKeys.PICKUP)
                        collected_this_frame.append(c)
                        self.player.oxygen = min(
                            self.player.oxygen + 5, gameplay.PLAYER_MAX_OXYGEN
                        )
                    else:
                        self.notification_message = "Недостаточно места в инвентаре!"
                        self.notification_time = gameplay.NOTIF_TIME

        if collected_this_frame:
            for c in collected_this_frame:
                if c in self.collectibles:
                    self.collectibles.remove(c)
            self._update_spatial_index()

        self.npc_manager.update_npc_visibility(self.player)
        self.storyteller_in_range = (
            self.npc_manager.get_nearby_storyteller(self.player) is not None
        )

        for npc in self.npcs:
            npc.update(self.player)