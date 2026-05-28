# entities/player.py
import pygame
import config

class Player:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.width = 24
        self.height = 24
        self.speed = config.PLAYER_MOVE_SPEED
        self.oxygen = config.PLAYER_MAX_OXYGEN
        self.rect = pygame.Rect(x - self.width//2, y - self.height//2, self.width, self.height)
        self.inventory = []
        self.max_weight = 20
        self.current_weight = 0
        self.entry_position = None
        
    def can_pickup(self, item) -> bool:
        """Может ли игрок поднять предмет"""
        return self.current_weight + item.weight <= self.max_weight
    
    def pickup(self, item) -> bool:
        """Подбор предмета"""
        if not self.can_pickup(item):
            return False
        
        self.inventory.append(item)
        self.current_weight += item.weight
        
        # Вес замедляет игрока
        speed_penalty = self.current_weight / self.max_weight
        self.speed = self.speed * (1 - speed_penalty * 0.5)
        
        return True
    
    def drop_item(self, index: int) -> bool:
        """Выбрасывает предмет"""
        if 0 <= index < len(self.inventory):
            item = self.inventory.pop(index)
            self.current_weight -= item.weight
            return True
        return False
    
    def calculate_score(self) -> int:
        """Считает общую ценность собранного"""
        return sum(item.value for item in self.inventory)
    
    def handle_input(self, keys: dict, walls: list) -> None:
        
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