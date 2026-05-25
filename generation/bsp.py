import random
from config import MIN_SIZE, SPLIT_RATIO_MIN, SPLIT_RATIO_MAX, RATIO_LIMIT
from typing import List, Tuple

class BSPNode:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y

        self.width = width
        self.height = height

        self.left: "BSPNode | None" = None
        self.right: "BSPNode | None" = None 

        self.room: Tuple[int, int, int, int] = None

    def split(self) -> bool:

        if self.width < MIN_SIZE or self.height < MIN_SIZE:
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
        if depth <= 0 or not self.split():
            return
        
        self.left.recursive_split(depth - 1)
        self.right.recursive_split(depth - 1)

    def get_leaf_nodes(self) -> List["BSPNode"]:
        if self.left is None and self.right is None:
            return [self]
        
        leaves: List[BSPNode] = []
        if self.left:
            leaves.extend(self.left.get_leaf_nodes())
        if self.right:
            leaves.extend(self.right.get_leaf_nodes())
        return leaves
    
    def create_room(self):

        if self.left or self.right:
            return
        
        room_margin = 6

        room_width = random.randint(int(self.width * 0.3), self.width - room_margin)
        room_height = random.randint(int(self.height * 0.3), self.height - room_margin)
        print(room_width, room_height)
        room_x = random.randint(self.x + room_margin, self.x + self.width - room_width - 6)
        room_y = random.randint(self.y + room_margin, self.y + self.height - room_height - 6)

        self.room = (room_x, room_y, room_width, room_height)
        print(self.room)

    def create_rooms_recursive(self):
        if self.left is None and self.right is None:
            self.create_room()
        else:
            if self.left:
                self.left.create_rooms_recursive()
            if self.right:
                self.right.create_rooms_recursive()

    def get_room(self):

        if self.room:
            return self.room

        rooms = []

        if self.left:
            room = self.left.get_room()

            if room:
                rooms.append(room)

        if self.right:
            room = self.right.get_room()

            if room:
                rooms.append(room)

        if rooms:
            return random.choice(rooms)

        return None


    def generate_corridors(self):
        corridors = []

        if self.left and self.right:
            corridors.extend(self.left.generate_corridors())
            corridors.extend(self.right.generate_corridors())

            room_a = self.left.get_room()
            room_b = self.right.get_room()

            if room_a and room_b:
                x1 = room_a[0] + room_a[2] // 2
                y1 = room_a[1] + room_a[3] // 2

                x2 = room_b[0] + room_b[2] // 2
                y2 = room_b[1] + room_b[3] // 2

                if random.random() < 0.5:
                    corridors.append((x1, y1, x2, y1))
                    corridors.append((x2, y1, x2, y2))
                else:
                    corridors.append((x1, y1, x1, y2))
                    corridors.append((x1, y2, x2, y2))

        return corridors