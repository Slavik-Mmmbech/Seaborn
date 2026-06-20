# entities/player.py
import pygame
from config.gameplay_config import PLAYER_MAX_OXYGEN, PLAYER_MOVE_SPEED, INVENTORY_MAX_WEIGHT


class Player:
    """Модуль игрока."""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.width = 24
        self.height = 24
        self.base_speed = PLAYER_MOVE_SPEED
        self.speed = PLAYER_MOVE_SPEED
        self.oxygen = float(PLAYER_MAX_OXYGEN)
        self.rect = pygame.Rect(
            int(x - self.width // 2), int(y - self.height // 2),
            self.width, self.height
        )
        self.inventory = []
        self.max_weight = INVENTORY_MAX_WEIGHT
        self.current_weight = 0
        self.entry_position = None

    def can_pickup(self, item) -> bool:
        """Может ли игрок поднять предмет, исходя из его веса.

        Attributes:
            item: Предмет.

        Returns:
            True/False: Возможно ли поднять предмет.
        """
        return self.current_weight + item.weight <= self.max_weight

    def pickup(self, item) -> bool:
        """Подбор предмета и замедление скорости.

        Attributes:
            item: Предмет.

        Returns:
            True/False
        """
        if not self.can_pickup(item):
            return False

        self.inventory.append(item)
        self.current_weight += item.weight

        speed_penalty = self.current_weight / self.max_weight
        self.speed = self.base_speed * (1 - speed_penalty * 0.5)

        return True

    def drop_item(self, index: int) -> bool:
        """Выбрасывает предмет
        
        ???
        """
        if 0 <= index < len(self.inventory):
            item = self.inventory.pop(index)
            self.current_weight -= item.weight
            # Recalculate speed after dropping
            speed_penalty = self.current_weight / self.max_weight
            self.speed = self.base_speed * (1 - speed_penalty * 0.5)
            return True
        return False

    def calculate_score(self) -> int:
        """Считает общую ценность собранного."""
        score = sum(item.value for item in self.inventory)
        return score

    def handle_input(self, keys: dict, walls: list) -> None:
        "Движение игрока"
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.y -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.y += self.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.x -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.x += self.speed

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
