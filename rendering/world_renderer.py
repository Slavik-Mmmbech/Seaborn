"""Рендерер для игрового мира - отрисовка статических элементов."""
import pygame
from rendering.npc_renderer import NPCRenderer
from rendering.player_renderer import PlayerRenderer
from rendering.collectible_renderer import CollectibleRenderer
from rendering.dungeon_renderer import DungeonRenderer
from lighting.lightmap_raycasting import LightSource
import config.display_config as display
import config.gameplay_config as gameplay

class WorldRenderer:
    """Отвечает за отрисовку статических элементов мира."""
    
    def __init__(self):
        self.npc_renderer = NPCRenderer()
        self.player_renderer = PlayerRenderer()
        self.collectible_renderer = CollectibleRenderer()
        self.dungeon_renderer = DungeonRenderer()
    
    def draw_world(self, screen: pygame.Surface, world) -> None:
        self.dungeon_renderer.draw_corridors(screen, world.corridors)
        self.dungeon_renderer.draw_rooms(screen, world.rooms)
        self.dungeon_renderer.draw_walls(screen, world.walls)
        
        # 2. Отрисовка динамических объектов
        if world.player:
            self.player_renderer.draw(screen, world.player)
        
        for npc in world.npcs:
            self.npc_renderer.draw(screen, npc)
        
        for c in world.collectibles:
            self.collectible_renderer.draw(screen, c)
        
        # 3. Эффект освещения
        self._render_light_mask(screen, world)

    def _render_light_mask(self, screen: pygame.Surface, world) -> None:
        if world.raycaster is None or world.player is None:
            return
        source = LightSource(
            world.player.rect.centerx, world.player.rect.centery, gameplay.LIGHT_RADIUS_BASE
        )
        polygon = world.raycaster.compute_visibility_polygon(source)
        if len(polygon) < 3:
            return

        dark_overlay = pygame.Surface(
            (display.SCREEN_WIDTH, display.SCREEN_HEIGHT), pygame.SRCALPHA
        )
        dark_overlay.fill((0, 0, 0, 210))
        pygame.draw.polygon(dark_overlay, (0, 0, 0, 0), polygon)
        screen.blit(dark_overlay, (0, 0))
