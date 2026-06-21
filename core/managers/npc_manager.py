import random
from typing import List, Tuple
import pygame
import ai
from entities.npc import NPC, NPCType
from loot.weighted_binary import WeightedBinaryLootGenerator
import config.gameplay_config as gameplay

class NPCManager:
    """Управление жизненным циклом, генерацией и поведением неигровых персонажей (NPC)."""
    
    def __init__(self, entry_point: Tuple[int, int], audio_manager=None):
        """
        :param entry_point: Точка появления игрока (используется для расчета безопасного расстояния).
        :param audio_manager: Опциональный менеджер звукового сопровождения.
        """
        self.entry_point = entry_point
        self.audio = audio_manager
        self.npcs: List[NPC] = []
        self.active_storyteller = None
        
    def spawn_all_npcs(self, rooms: List[pygame.Rect], 
                       build_lore_chain_func,
                       create_behavior_tree_func) -> None:
        """Инициализирует и спавнит все группы NPC по соответствующим пулам комнат."""
        self.npcs = []
        
        if not rooms:
            return
            
        # Спавн Атакующих NPC
        self._spawn_npc_type(
            rooms=rooms[gameplay.ATTACKER_ROOM_INDICES],
            npc_type=NPCType.ATTACKER,
            prefix="attacker",
            build_lore_chain=build_lore_chain_func,
            create_behavior_tree=create_behavior_tree_func
        )
        
        # Спавн Убегающих NPC
        self._spawn_npc_type(
            rooms=rooms[gameplay.ESCAPER_ROOM_INDICES],
            npc_type=NPCType.ESCAPER,
            prefix="escaper",
            build_lore_chain=build_lore_chain_func,
            create_behavior_tree=create_behavior_tree_func
        )
        
        # Спавн Рассказчиков NPC
        storyteller_rooms = self._filter_storyteller_rooms(rooms)
        self._spawn_npc_type(
            rooms=storyteller_rooms,
            npc_type=NPCType.STORYTELLER,
            prefix="storyteller",
            build_lore_chain=build_lore_chain_func,
            create_behavior_tree=create_behavior_tree_func,
            with_rewards=True
        )
    
    def _filter_storyteller_rooms(self, rooms: List[pygame.Rect]) -> List[pygame.Rect]:
        """Отбирает удаленные от старта комнаты для размещения Storyteller."""
        start_idx = gameplay.STORYTELLER_ROOM_START_INDEX
        filtered = [
            room for room in rooms[start_idx:]
            if self._calculate_distance(self.entry_point, room.center) 
            > gameplay.STORYTELLER_MIN_DISTANCE_FROM_ENTRY
        ]
        return filtered[:gameplay.STORYTELLER_ROOM_COUNT]
    
    def _spawn_npc_type(self, rooms: List[pygame.Rect], 
                       npc_type: NPCType,
                       prefix: str,
                       build_lore_chain,
                       create_behavior_tree,
                       with_rewards: bool = False) -> None:
        """Внутренний фабричный метод для унифицированного создания сущностей NPC."""
        for idx, room in enumerate(rooms):
            spawn_pos = self._calculate_spawn_position(room)
            lore_chain = build_lore_chain()
            
            npc = NPC(
                npc_id=f"{prefix}_{idx + 1}",
                start_pos=spawn_pos,
                bt_root=ai.Action(lambda bb: ai.NodeStatus.SUCCESS),
                lore_chain=lore_chain,
                npc_type=npc_type,
            )
            npc.bt_root = create_behavior_tree(npc)
            
            if with_rewards:
                npc.dialog_rewards = WeightedBinaryLootGenerator(
                    gameplay.LOOT_REWARDS
                )
            
            self.npcs.append(npc)
    
    def _calculate_spawn_position(self, room: pygame.Rect) -> Tuple[int, int]:
        """Рассчитывает случайную позицию около центра комнаты в пределах заданного радиуса."""
        spawn_x = room.centerx + random.randint(
            -gameplay.NPC_SPAWN_RANDOM_RANGE,
            gameplay.NPC_SPAWN_RANDOM_RANGE
        )
        spawn_y = room.centery + random.randint(
            -gameplay.NPC_SPAWN_RANDOM_RANGE,
            gameplay.NPC_SPAWN_RANDOM_RANGE
        )
        return (spawn_x, spawn_y)
    
    def _calculate_distance(self, point1, point2) -> float:
        """Евклидово расстояние между двумя точками."""
        return ((point1[0] - point2[0]) ** 2 + 
                (point1[1] - point2[1]) ** 2) ** 0.5
    
    def update_npc_visibility(self, player) -> None:
        """Обновляет состояние Blackboard каждого NPC в зависимости от видимости игрока."""
        if not player:
            return
            
        for npc in self.npcs:
            distance = self._calculate_distance(npc.position, player.rect.center)
            
            if npc.npc_type in (NPCType.ATTACKER, NPCType.ESCAPER):
                sees_player = distance <= gameplay.NPC_SEE_DISTANCE
            elif npc.npc_type == NPCType.STORYTELLER:
                sees_player = distance <= gameplay.NPC_TALK_DISTANCE
            else:
                sees_player = False
                
            npc.blackboard.set("sees_player", sees_player)
    
    def get_nearby_storyteller(self, player) -> NPC | None:
        """Возвращает ссылку на Storyteller, если игрок находится в радиусе ведения диалога."""
        if not player:
            return None
            
        for npc in self.npcs:
            if npc.npc_type != NPCType.STORYTELLER:
                continue
            distance = self._calculate_distance(player.rect.center, npc.position)
            if distance <= gameplay.NPC_TALK_DISTANCE:
                return npc
        return None