import pygame
import config
from core.world import World

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.world = World()
        self.world.generate() # type: ignore

    def run(self):
        running = True

        while running:
            self.clock.tick(config.FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            keys = pygame.key.get_pressed()

            self.world.update(keys) # type: ignore

            self.screen.fill(config.WATER_COLOR)
            self.world.draw(self.screen) # type: ignore

            pygame.display.flip()

