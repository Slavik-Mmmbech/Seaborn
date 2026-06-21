import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
import random
from generation.bsp_tree import BSPNode
from generation.room_generator import RoomGenerator
from generation.corridor_generator import CorridorGenerator

@pytest.fixture(autouse=True)
def seed_random():
    random.seed(42)

@pytest.fixture
def bsp_root():
    return BSPNode(0, 0, 800, 600)

@pytest.fixture
def prepared_bsp_tree(bsp_root):
    bsp_root.left = BSPNode(0, 0, 400, 600)
    bsp_root.right = BSPNode(400, 0, 400, 600)
    
    bsp_root.left.left = BSPNode(0, 0, 200, 300)
    bsp_root.left.right = BSPNode(0, 300, 200, 300)
    
    bsp_root.left.left.room = (10, 10, 50, 50)
    bsp_root.left.right.room = (10, 310, 50, 50)
    bsp_root.right.room = (410, 10, 50, 50)
    
    return bsp_root

@pytest.fixture
def room_generator():
    return RoomGenerator(min_fill_ratio=0.5)
