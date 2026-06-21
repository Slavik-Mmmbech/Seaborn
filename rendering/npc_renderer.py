import pygame
from config.display_config import (
    NPC_COLORS,
    BASE_COLOR,
    DEFAULT_COLOR,
    LABEL_COLOR,
    NPC_LABEL_DELTA,
)
from config.enums import NPCType
from config.gameplay_config import (
    NPC_LABEL_FONT_SIZE,
    NPC_TYPE_MARKER_FONT_SIZE
)


class NPCRenderer:
    """Отвечает за визуальное представление NPC."""

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
        npc_color = NPC_COLORS.get(npc.npc_type, DEFAULT_COLOR)
        pygame.draw.circle(surface, npc_color, npc.rect.center, npc.radius)

        self._draw_label(surface, npc)

        if npc.npc_type == NPCType.STORYTELLER:
            self._draw_storyteller_marker(surface, npc)

    def _draw_label(self, surface: pygame.Surface, npc) -> None:
        """Отрисовка текстовой метки NPC."""
        label = self.label_font.render(npc.id, True, LABEL_COLOR)
        label_pos = (
            npc.rect.centerx - label.get_width() // 2,
            npc.rect.top - NPC_LABEL_DELTA,
        )
        surface.blit(label, label_pos)

    def _draw_storyteller_marker(self, surface: pygame.Surface, npc) -> None:
        """Отрисовка специального маркера для Storyteller."""
        mark = self.marker_font.render("?", True, BASE_COLOR)
        mark_pos = (
            npc.rect.centerx - mark.get_width() // 2,
            npc.rect.centery - mark.get_height() // 2,
        )
        surface.blit(mark, mark_pos)
