import pygame
import config
from core.world import World
# Слабая имплементация модулей, интегрирование алгоритмов в
# игровой процесс в будущем.
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        )
        pygame.display.set_caption("Deep Dive: Risk & Reward")
        self.clock = pygame.time.Clock()
        self.world = World()
        self.world.generate()
        self.debug_mode = True
        self.running = True

    def run(self):
        while self.running:
            self.clock.tick(config.FPS)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_l:
                        self.debug_mode = not self.debug_mode
                    if event.key == pygame.K_r:
                        self.world.generate()
                    if event.key == pygame.K_ESCAPE:
                        self.running = False

            keys = pygame.key.get_pressed()
            self.world.update(keys)

            self.screen.fill(config.WATER_COLOR)
            self.world.draw(self.screen)
            self.draw_ui(self.screen)

            pygame.display.flip()

        pygame.quit()

    def draw_ui(self, screen):
        """Отрисовка интерфейса"""
        if not self.world.player:
            return
            
        font = pygame.font.Font(None, 36)
        small_font = pygame.font.Font(None, 24)
        
        oxygen = self.world.player.oxygen
        oxygen_color = (255, 255, 255) if oxygen > 30 else (255, 100, 0)
        oxygen_text = font.render(
            f"Oxygen: {int(oxygen)}", True, oxygen_color
        )
        screen.blit(oxygen_text, (10, 10))
        
        if hasattr(self.world.player, 'inventory'):
            inv_text = small_font.render(
                f"Items: {len(self.world.player.inventory)}", 
                True, (255, 255, 255)
            )
            screen.blit(inv_text, (10, 50))
        
        # Подсказки
        hints = [
            "WASD/Arrows - Move",
            "R - Regenerate",
            "D - Debug mode",
            "ESC - Quit"
        ]
        for i, hint in enumerate(hints):
            text = small_font.render(hint, True, (200, 200, 200))
            screen.blit(text, (config.SCREEN_WIDTH - 150, 10 + i * 20))
        
        # Game Over
        if oxygen <= 0:
            overlay = pygame.Surface(
                (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
            )
            overlay.fill((0, 0, 0))
            overlay.set_alpha(128)
            screen.blit(overlay, (0, 0))
            
            game_over = font.render("GAME OVER", True, (255, 0, 0))
            restart = small_font.render(
                "Press R to restart or ESC to quit", True, (255, 255, 255)
            )
            
            screen.blit(game_over, 
                       (config.SCREEN_WIDTH//2 - 80, config.SCREEN_HEIGHT//2 - 30))
            screen.blit(restart,
                       (config.SCREEN_WIDTH//2 - 120, config.SCREEN_HEIGHT//2 + 10))