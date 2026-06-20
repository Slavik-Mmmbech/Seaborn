# core/world.py
import math
import pygame
import random
from typing import List

import ai
import config.display_config as display
import config.gameplay_config as gameplay
import config.generation_config as gen
import config.content_config as content
from entities.npc import NPC, NPCType
from entities.player import Player
from entities.items import Collectible
from entities.items import Item
from generation.dungeon import DungeonGenerator
from lighting.lightmap_raycasting import LightSource, Raycaster
from spatial.quadtree import QuadTree, Bounds
from loot.loot_bag import LootBag
from loot.weighted_binary import WeightedBinaryLootGenerator
from config.logging_config import setup_logger

logger = setup_logger(__name__)


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
        self.npcs: List[NPC] = []
        self.entry_point = None  # Где начал игрок
        self.exit_rect = None  # Зона выхода
        self.is_returning = False
        self.light_grid: List[List[int]] = []
        self.raycaster: Raycaster | None = None
        self.level_index = 0
        self.completed_levels = 0
        self.story_mode_active = False
        self.active_storyteller: NPC | None = None
        self.talk_text = ""
        self.notification_message = ""
        self.notification_time = 0.0  # Timer for notification display
        self.player_in_exit_zone = False

        world_bounds = Bounds(0, 0, display.SCREEN_WIDTH, display.SCREEN_HEIGHT)
        self.spatial_index = QuadTree(
            world_bounds,
            max_capacity=gen.MAX_CAPACITY,
            max_depth=gen.MAX_DEPTH
        )
        self.level_complete = False
        logger.info("ГЕНЕРАЦИЯ МИРА ПРОШЛА УСПЕШНО. УДАЧИ!")

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
        return (
            (point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2
            ) ** 0.5

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

        dg = DungeonGenerator(display.SCREEN_WIDTH,
                              display.SCREEN_HEIGHT,
                              depth=4
                              )
        self.rooms, self.corridors = dg.generate()

        self._build_walkable_areas()
        self._generate_walls_from_geometry()
        self._build_light_grid()

        if self.rooms:
            start_room = self.rooms[0]
            self.player = Player(start_room.centerx, start_room.centery)
            self.entry_point = start_room.center
            self.exit_rect = start_room.copy()
            self.exit_rect.inflate_ip(-20, -20)

        self._assign_room_values()
        self._spawn_collectibles()
        self._spawn_npcs()
        self.level_complete = False
        logger.debug(f"Сгенерированы NPC: {self.npcs}")

    def _build_walkable_areas(self) -> None:
        """Создает список всех проходимых зон (комнаты + коридоры)"""
        self.walkable_areas = []

        # Добавление комнат.
        for room in self.rooms:
            self.walkable_areas.append(room.copy())

        # Преобразование коридоров в прямоугольники.
        for corridor in self.corridors:
            x1, y1, x2, y2 = corridor
            # Создание прямоугольника коридора.
            corridor_rect = pygame.Rect(
                min(x1, x2) - 12, min(y1, y2) - 12,
                abs(x2 - x1) + 24, abs(y2 - y1) + 24
            )
            self.walkable_areas.append(corridor_rect)

    def _generate_walls_from_walkable_areas(self) -> None:
        """Создает стены как границы проходимых зон + границы экрана"""
        self.walls = []

        # 1. Границы экрана
        border_thickness = 4
        screen_borders = [
            pygame.Rect(0, 0, display.SCREEN_WIDTH, border_thickness),
            pygame.Rect(
                0,
                display.SCREEN_HEIGHT - border_thickness,
                display.SCREEN_WIDTH,
                border_thickness,
            ),
            pygame.Rect(0, 0, border_thickness, display.SCREEN_HEIGHT),
            pygame.Rect(
                display.SCREEN_WIDTH - border_thickness,
                0,
                border_thickness,
                display.SCREEN_HEIGHT,
            ),
        ]
        self.walls.extend(screen_borders)

    def _is_position_valid(self, rect: pygame.Rect) -> bool:
        """Проверяет, находится ли центр игрока в проходимой зоне"""
        if not self.walkable_areas:
            return False

        # Создание точки в центре игрока для проверки
        center_x = rect.centerx
        center_y = rect.centery
        point_rect = pygame.Rect(center_x - 2, center_y - 2, 4, 4)

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

        room_weights = [
            self.room_values.get(i, 0.0) for i in range(len(self.rooms))]

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
                random.uniform(10.0, 25.0) * value_mult,
            )

            room = random.choices(self.rooms, weights=room_weights)[0]

            padding = gen.ROOM_OFFSET
            min_x, max_x = room.left + padding, room.right - padding
            min_y, max_y = room.top + padding, room.bottom - padding

            safe_x = min_x if max_x <= min_x else random.randint(min_x, max_x)
            safe_y = min_y if max_y <= min_y else random.randint(min_y, max_y)

            new_collectibles.append(Collectible(safe_x, safe_y, item))

        self.collectibles.extend(new_collectibles)
        logger.info(f"Предметы были распределены.")
        self._update_spatial_index()

    def draw_debug(self, screen: pygame.Surface) -> None:
        """Отрисовка BSP структуры для отладки"""
        debug_surface = pygame.Surface((display.SCREEN_WIDTH, display.SCREEN_HEIGHT))
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
            f"Кол-во предметов - {self.collected_items})",
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
        self.walls.extend(
            [
                pygame.Rect(0, 0, display.SCREEN_WIDTH, border_thickness),
                pygame.Rect(
                    0,
                    display.SCREEN_HEIGHT - border_thickness,
                    display.SCREEN_WIDTH,
                    border_thickness,
                ),
                pygame.Rect(0, 0, border_thickness, display.SCREEN_HEIGHT),
                pygame.Rect(
                    display.SCREEN_WIDTH - border_thickness,
                    0,
                    border_thickness,
                    display.SCREEN_HEIGHT,
                ),
            ]
        )

    def _build_light_grid(self) -> None:
        """Строит сетку препятствий для светового рендеринга."""
        grid_width = display.SCREEN_WIDTH // display.TILE_SIZE
        grid_height = display.SCREEN_HEIGHT // display.TILE_SIZE
        self.light_grid = [[1] * grid_width for _ in range(grid_height)]

        for gy in range(grid_height):
            for gx in range(grid_width):
                cell_center = (
                    gx * display.TILE_SIZE + display.TILE_SIZE / 2,
                    gy * display.TILE_SIZE + display.TILE_SIZE / 2,
                )
                if any(area.collidepoint(cell_center) for area in self.walkable_areas):
                    self.light_grid[gy][gx] = 0

        self.raycaster = Raycaster(self.light_grid, display.TILE_SIZE)

    def _spawn_npcs(self) -> None:
        """
        Создаёт несколько NPC внутри комнат и
        связывает их с деревом поведения.
        """
        self.npcs = []
        self.active_storyteller = None
        self.talk_text = ""
        self.storyteller_in_range = False

        if not self.rooms:
            return

        attacker_rooms = self.rooms[2:4]
        escaper_rooms = self.rooms[4:6]
        storyteller_rooms = [
            room
            for room in self.rooms[6:]
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
            dialog_rewards = WeightedBinaryLootGenerator(
                gameplay.LOOT_REWARDS
            )
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

    def _render_light_mask(self, screen: pygame.Surface) -> None:
        if self.raycaster is None or self.player is None:
            return

        source = LightSource(
            self.player.rect.centerx, self.player.rect.centery, gameplay.LIGHT_RADIUS_BASE
        )
        polygon = self.raycaster.compute_visibility_polygon(source)
        if len(polygon) < 3:
            return

        dark_overlay = pygame.Surface(
            (display.SCREEN_WIDTH, display.SCREEN_HEIGHT), pygame.SRCALPHA
        )
        dark_overlay.fill((0, 0, 0, 210))
        pygame.draw.polygon(dark_overlay, (0, 0, 0, 0), polygon)
        screen.blit(dark_overlay, (0, 0))

    # Использование QuadTree снижает сложность поиска пересекающихся объектов
    # с O(N) до O(log N), что критично для производительности при большом
    # количестве сущностей на карте.
    def update(self, keys: dict) -> None:
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

        self.player.handle_input(keys, [])

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
                npc.blackboard.set("sees_player", distance <= gameplay.NPC_TALK_DISTANCE)

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
            npc.update(1 / display.FPS)

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill(display.WATER_COLOR)

        floor_color = display.FLOOR_COLOR
        for area in self.walkable_areas:
            pygame.draw.rect(screen, floor_color, area)

        wall_color = display.WALL_COLOR
        for room in self.rooms:
            pygame.draw.rect(screen, wall_color, room, width=1)

        if self.player:
            pygame.draw.rect(screen, display.PLAYER_COLOR, self.player.rect)

        for npc in self.npcs:
            npc.draw(screen)

        for c in self.collectibles:
            c.draw(screen)

        if self.exit_rect:
            pygame.draw.rect(screen, display.EXIT_COLOR, self.exit_rect, width=2)

        self._render_light_mask(screen)
