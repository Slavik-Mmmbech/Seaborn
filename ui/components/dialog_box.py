"""Компонент окна диалога для общения с NPC."""
import pygame
import config.display_config as display


class DialogBox:
    """Отрисовывает черное окно с текстом и рамкой."""

    def __init__(self, screen_width: int, screen_height: int):
        self.rect = pygame.Rect(
            70, screen_height - 160, screen_width - 140, 120
        )
        self.font = pygame.font.Font(None, 24)
        self.close_hint_font = pygame.font.Font(None, 20)

    def draw(self, surface: pygame.Surface, text: str) -> None:
        if not text:
            return

        # Фон и рамка
        pygame.draw.rect(surface, (0, 0, 0), self.rect)
        pygame.draw.rect(surface, display.BASE_COLOR, self.rect, 2)

        # Подсказка закрытия
        hint = self.close_hint_font.render(
            "SPACE / E - закрыть", True, display.BASE_COLOR
        )
        surface.blit(hint, (self.rect.x + 10, self.rect.y + 10))

        # Отрисовка текста с переносом
        self._draw_wrapped_text(surface, text)

    def _draw_wrapped_text(self, surface: pygame.Surface, text: str) -> None:
        words = text.split(" ")
        lines = []
        current_line = ""

        for word in words:
            test_line = f"{current_line} {word}" if current_line else word
            if self.font.size(test_line)[0] <= self.rect.width - 20:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        y = self.rect.y + 40
        for line in lines:
            rendered = self.font.render(line, True, (220, 220, 220))
            surface.blit(rendered, (self.rect.x + 10, y))
            y += self.font.get_linesize()
            if y > self.rect.bottom - 10:
                break