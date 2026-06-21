import pygame
from config.enums import NPCType
from config.gameplay_config import NPC_LABEL_FONT_SIZE, NPC_TYPE_MARKER_FONT_SIZE
from typing import Dict, Tuple

class NPCRenderer:
    """Отвечает за визуальное представление NPC."""

    NPC_COLORS: Dict[NPCType, Tuple[int, int, int]] = {
        NPCType.ATTACKER: (220, 80, 80),      # Красный
        NPCType.ESCAPER: (80, 180, 220),      # Голубой
        NPCType.STORYTELLER: (190, 190, 90),  # Жёлтый
    }
    
    LABEL_COLOR = (235, 235, 235)
    MARKER_COLOR = (255, 255, 255)
    DEFAULT_COLOR = (220, 80, 80)
    
    def __init__(self):
        """Инициализация шрифтов."""
        if not pygame.font.get_init():
            pygame.font.init()

        self.label_font = pygame.font.Font(None, NPC_LABEL_FONT_SIZE)
        self.marker_font = pygame.font.Font(None, NPC_TYPE_MARKER_FONT_SIZE)
        
            
    def draw(self, surface: pygame.Surface, npc) -> None:
        """
        Отрисовка NPC.
        
        Args:
            surface: Поверхность для отрисовки
            npc: Экземпляр NPC для отрисовки
        """
        # 1. Рисуем тело NPC
        npc_color = self.NPC_COLORS.get(npc.npc_type, self.DEFAULT_COLOR)
        pygame.draw.circle(
            surface, 
            npc_color, 
            npc.rect.center, 
            npc.radius
        )

        self._draw_label(surface, npc)

        if npc.npc_type == NPCType.STORYTELLER:
            self._draw_storyteller_marker(surface, npc)
    
    def _draw_label(self, surface: pygame.Surface, npc) -> None:
        """Отрисовка текстовой метки NPC."""
        label = self.label_font.render(
            npc.id, 
            True, 
            self.LABEL_COLOR
        )
        label_pos = (
            npc.rect.centerx - label.get_width() // 2,
            npc.rect.top - 18
        )
        surface.blit(label, label_pos)

    def _draw_storyteller_marker(self, surface: pygame.Surface, npc) -> None:
        """Отрисовка специального маркера для Storyteller."""
        mark = self.marker_font.render(
            "?", 
            True, 
            self.MARKER_COLOR
        )
        mark_pos = (
            npc.rect.centerx - mark.get_width() // 2,
            npc.rect.centery - mark.get_height() // 2
        )
        surface.blit(mark, mark_pos)