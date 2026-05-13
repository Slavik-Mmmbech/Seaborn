import random
from config import MIN_SIZE, SPLIT_RATIO_MIN, SPLIT_RATIO_MAX, RATIO_LIMIT

class BSPNode:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y

        self.width = width
        self.height = height

        self.left = None
        self.right = None

    def split(self):

        if self.width < MIN_SIZE * 2 or self.height < MIN_SIZE * 2:\
            return False

        if self.width / self.height >= RATIO_LIMIT:
            split_horizontally = False

        elif self.height / self.width >= RATIO_LIMIT:
            split_horizontally = True

        else:
            split_horizontally = random.choice([True, False])

        if split_horizontally:
            min_split = int(self.height * SPLIT_RATIO_MIN)
            max_split = int(self.height * SPLIT_RATIO_MAX)
            split = random.randint(min_split, max_split)

            self.left = BSPNode(
                self.x,
                self.y,
                self.width,
                split
            )

            self.right = BSPNode(
                self.x,
                self.y + split,
                self.width,
                self.height - split
            )
        
        else:
            min_split = int(self.width * SPLIT_RATIO_MIN)
            max_split = int(self.width * SPLIT_RATIO_MAX)
            split = random.randint(min_split, max_split)

            self.left = BSPNode(
                self.x,
                self.y,
                split,
                self.height
            )

            self.right = BSPNode(
                self.x + split,
                self.y,
                self.width - split,
                self.height
            )

            return True

    def recursive_split(self, depth):
        if depth <= 0:
            return
        
        if not self.split():
            return 
        
        self.left.recursive_split(depth-1)
        self.right.recursive_split(depth-1)

    def get_leaf_nodes(self):
        if self.left is None and self.right is None:
            return [self]
        
        leaves = []

        if self.left:
            leaves.extend(self.left.get_leaf_nodes())
        
        if self.right:
            leaves.extend(self.right.get_leaf_nodes())

        return leaves