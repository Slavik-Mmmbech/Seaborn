"""Модуль рендеринга игровых сущностей."""
from rendering.npc_renderer import NPCRenderer
from rendering.player_renderer import PlayerRenderer
from rendering.collectible_renderer import CollectibleRenderer
from rendering.world_renderer import WorldRenderer
from rendering.dungeon_renderer import DungeonRenderer

__all__ = [
    'NPCRenderer',
    'PlayerRenderer', 
    'CollectibleRenderer',
    'WorldRenderer',
    'DungeonRenderer'
]