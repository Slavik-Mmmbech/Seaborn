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
        self._spawn_collectibles()
        self._spawn_npcs()
        self.level_complete = False
        logger.debug(f"Сгенерированы NPC: {self.npcs}")

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

    def _is_position_valid(self, rect: pygame.Rect) -> bool:
        """Проверяет, находится ли центр игрока в проходимой зоне"""
        if not self.walkable_areas:
            return False

        # Создание точки в центре игрока для проверки
        center_x = rect.centerx
        center_y = rect.centery
        point_rect = pygame.Rect(center_x - gameplay.VALID_DELTA,
                                 center_y - gameplay.VALID_DELTA,
                                 gameplay.VALID_SIZE,
                                 gameplay.VALID_SIZE
                                 )

        for area in self.walkable_areas:
            if point_rect.colliderect(area):
                return True
        return False

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

    def _spawn_collectibles(self) -> None:
        """Размещает предметы внутри границ комнат с отступом."""
        if not self.rooms:
            return

        bag = LootBag()
        new_collectibles = []

        room_weights = [self.room_values.get(i, 0.0) for i in range(len(self.rooms))]

        if sum(room_weights) == 0:
            room_weights = [1.0] * len(self.rooms)

        for _ in range(30):
            rarity = bag.draw()

            rarity_cfg = gameplay.ITEM_RARITY_CONFIG[rarity]
            min_w, max_w, value_mult, _ = rarity_cfg
            item = Item(
                "loot",
                rarity,
                random.uniform(min_w, max_w),
                random.uniform(gameplay.LOW_VALUE,
                               gameplay.HIGH_VALUE
                               ) * value_mult,
            )

            room_data = random.choices(self.rooms, weights=room_weights)[0]

            room = pygame.Rect(*room_data)

            padding = gen.ROOM_OFFSET
            min_x, max_x = room.left + padding, room.right - padding
            min_y, max_y = room.top + padding, room.bottom - padding

            safe_x = min_x if max_x <= min_x else random.randint(min_x, max_x)
            safe_y = min_y if max_y <= min_y else random.randint(min_y, max_y)

            new_collectibles.append(Collectible(safe_x, safe_y, item))

        self.collectibles.extend(new_collectibles)
        logger.info(f"Предметы были распределены.")
        self._update_spatial_index()

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

    def _spawn_npcs(self) -> None:
        """Создаёт несколько NPC внутри комнат."""
        self.npcs = []
        self.active_storyteller = None
        self.talk_text = " "
        self.storyteller_in_range = False

        if not self.rooms:
            return

        rooms_rects = [pygame.Rect(*room_data) for room_data in self.rooms]

        attacker_rooms = rooms_rects[2:4]
        escaper_rooms = rooms_rects[4:6]
        storyteller_rooms = [
            room
            for room in rooms_rects[6:]
            if self._calculate_distance(self.entry_point, room.center) > 240
        ][:2]

        for idx, room in enumerate(attacker_rooms):
            spawn_x = room.centerx + random.randint(-20, 20)
            spawn_y = room.centery + random.randint(-20, 20)
            lore_chain = self._build_lore_chain()
            npc = NPC(
                npc_id=f"attacker_{idx + 1}",
                start_pos=(spawn_x, spawn_y),
                bt_root=ai.Action(lambda bb: ai.NodeStatus.SUCCESS),
                lore_chain=lore_chain,
                npc_type=NPCType.ATTACKER,
            )
            npc.bt_root = self._create_npc_behavior_tree(npc)
            self.npcs.append(npc)

        for idx, room in enumerate(escaper_rooms):
            spawn_x = room.centerx + random.randint(-20, 20)
            spawn_y = room.centery + random.randint(-20, 20)
            lore_chain = self._build_lore_chain()
            npc = NPC(
                npc_id=f"escaper_{idx + 1}",
                start_pos=(spawn_x, spawn_y),
                bt_root=ai.Action(lambda bb: ai.NodeStatus.SUCCESS),
                lore_chain=lore_chain,
                npc_type=NPCType.ESCAPER,
            )
            npc.bt_root = self._create_npc_behavior_tree(npc)
            self.npcs.append(npc)

        for idx, room in enumerate(storyteller_rooms):
            spawn_x = room.centerx + random.randint(-20, 20)
            spawn_y = room.centery + random.randint(-20, 20)
            lore_chain = self._build_lore_chain()
            npc = NPC(
                npc_id=f"storyteller_{idx + 1}",
                start_pos=(spawn_x, spawn_y),
                bt_root=ai.Action(lambda bb: ai.NodeStatus.SUCCESS),
                lore_chain=lore_chain,
                npc_type=NPCType.STORYTELLER,
            )
            dialog_rewards = WeightedBinaryLootGenerator(gameplay.LOOT_REWARDS)
            npc.dialog_rewards = dialog_rewards
            npc.bt_root = self._create_npc_behavior_tree(npc)
            self.npcs.append(npc)

    def get_nearby_storyteller(self):
        if not self.player:
            return None

        for npc in self.npcs:
            if npc.npc_type != NPCType.STORYTELLER:
                continue
            distance = self._calculate_distance(self.player.rect.center, npc.position)
            if distance <= gameplay.NPC_TALK_DISTANCE:
                return npc
        return None

    def _build_lore_chain(self) -> ai.MarkovChain:
        transitions = content.GAME_TRANSITIONS
        return ai.MarkovChain(transitions)

    def _create_npc_behavior_tree(self, npc: NPC):
        def check_sees_player(bb):
            return bb.get("sees_player") is True

        def move_toward_player(bb):
            if self.player:
                npc.move_to(self.player.rect.center, max_step=npc.speed)
                return ai.NodeStatus.RUNNING
            return ai.NodeStatus.FAILURE

        def move_away_from_player(bb):
            if self.player:
                dx = npc.position[0] - self.player.rect.centerx
                dy = npc.position[1] - self.player.rect.centery
                distance = math.hypot(dx, dy)
                if distance < 1e-3:
                    return ai.NodeStatus.FAILURE
                target = (
                    npc.position[0] + dx / distance * npc.speed * 1.2,
                    npc.position[1] + dy / distance * npc.speed * 1.2,
                )
                npc.move_to(target, max_step=npc.speed)
                return ai.NodeStatus.RUNNING
            return ai.NodeStatus.FAILURE

        def patrol_action(bb):
            npc.patrol()
            return ai.NodeStatus.SUCCESS

        def storyteller_idle(bb):
            return ai.NodeStatus.SUCCESS

        if npc.npc_type == NPCType.ATTACKER:
            return ai.Selector(
                [
                    ai.Sequence(
                        [
                            ai.Condition(check_sees_player),
                            ai.Action(move_toward_player),
                        ]
                    ),
                    ai.Action(patrol_action),
                ]
            )

        if npc.npc_type == NPCType.ESCAPER:
            return ai.Selector(
                [
                    ai.Sequence(
                        [
                            ai.Condition(check_sees_player),
                            ai.Action(move_away_from_player),
                        ]
                    ),
                    ai.Action(patrol_action),
                ]
            )

        return ai.Selector(
            [
                ai.Action(storyteller_idle),
            ]
        )

    # Использование QuadTree снижает сложность поиска пересекающихся объектов
    # с O(N) до O(log N), что критично для производительности при большом
    # количестве сущностей на карте.
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

        if not self._is_position_valid(self.player.rect):
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

        self.storyteller_in_range = False
        for npc in self.npcs:
            if self.player:
                distance = self._calculate_distance(
                    npc.position,
                    self.player.rect.center,
                )
                if npc.npc_type == NPCType.ATTACKER:
                    npc.blackboard.set(
                        "sees_player", distance <= gameplay.NPC_SEE_DISTANCE
                    )
                elif npc.npc_type == NPCType.ESCAPER:
                    npc.blackboard.set(
                        "sees_player", distance <= gameplay.NPC_SEE_DISTANCE
                    )
                elif npc.npc_type == NPCType.STORYTELLER:
                    can_talk = distance <= gameplay.NPC_TALK_DISTANCE
                    npc.blackboard.set("sees_player", can_talk)
                    if can_talk:
                        self.storyteller_in_range = True
            npc.update()
