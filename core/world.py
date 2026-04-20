from entities.player import Player
from entities.collectible import Collectible
from generation.loot_bag import LootBag
import random

class World:
    def __init__(self):
        self.player = None
        self.collectibles = []
        self.walls = []
    
    def generate(self):
        self.player = Player(100,100)

        bag = LootBag()

        for _ in range(10):
            rarity = bag.draw()

            from entities.item import Item
            item = Item("loot", rarity, 7, 25)

            x = random.randint(50,500)
            y = random.randint(50,500)

            self.collectibles.append(Collectible(x, y, item))

    def update(self, keys):
        self.player.handle_input(keys, self.walls) # type: ignore
        
        for c in self.collectibles:
            if c.try_collect(self.player.rect): # type: ignore
                print("Collected:", c.item)

    def draw(self, screen):
        for c in self.collectibles:
            c.draw(screen)

        self.player.draw(screen) # type: ignore