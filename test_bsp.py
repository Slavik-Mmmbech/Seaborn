"""
Визуализатор BSP-генерации подземелья.
Демонстрирует пошаговое разбиение пространства, создание комнат и коридоров.
"""
import pygame
import time
from typing import List, Tuple
from generation.bsp_tree import BSPNode
from generation.room_generator import RoomGenerator
from generation.corridor_generator import CorridorGenerator
from config.display_config import SCREEN_HEIGHT, SCREEN_WIDTH

FRAMES_PER_STEP = 30
OFFSET_X, OFFSET_Y = 50, 50

class BSPVisualizer:
    """Оркестратор визуализации BSP-алгоритма."""
    
    def __init__(self, split_depth: int = 4):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("BSP Dungeon Generator Visualization")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Consolas", 16)

        self.colors = {
            "bg": (20, 20, 28),
            "split_line": (60, 100, 140),
            "room_fill": (60, 150, 100),
            "room_border": (255, 255, 255),
            "corridor": (30, 120, 30),
            "text": (240, 240, 240)
        }

        self.split_depth = split_depth
        self.reset()

    def reset(self) -> None:
        """Сбрасывает состояние генерации для нового запуска."""
        self.root = BSPNode(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.phase = "partition"
        self.current_level = 0
        self.rooms: List[pygame.Rect] = []
        self.corridors: List[Tuple[int, int, int, int]] = []
        self.frame_counter = 0

        # Генераторы
        self.room_gen = RoomGenerator()
        self.corridor_gen = CorridorGenerator(self.room_gen)

    def _advance_partition(self) -> None:
        """Делит все узлы на текущем уровне глубины."""
        nodes_to_split = []
        queue = [(self.root, 0)]
        while queue:
            node, depth = queue.pop(0)
            if depth == self.current_level:
                nodes_to_split.append(node)
            elif depth < self.current_level:
                if node.left: queue.append((node.left, depth + 1))
                if node.right: queue.append((node.right, depth + 1))

        for node in nodes_to_split:
            node.split()

        self.current_level += 1
        if self.current_level >= self.split_depth:
            self.phase = "rooms"

    def _generate_rooms(self) -> None:
        """Создает комнаты в листовых узлах."""
        self.room_gen.create_rooms_in_tree(self.root)
        leaves = self.root.get_leaf_nodes()
        self.rooms = [pygame.Rect(*n.room) for n in leaves if n.room]
        self.phase = "corridors"

    def _generate_corridors(self) -> None:
        """Соединяет комнаты коридорами."""
        self.corridors = self.corridor_gen.generate_corridors(self.root)
        self.phase = "done"

    def _draw_tree_borders(self, node: BSPNode) -> None:
        """Рекурсивно рисует границы BSP-разбиения."""
        if node is None:
            return
        rect = pygame.Rect(node.x, node.y, node.width, node.height)
        if not node.room:
            pygame.draw.rect(self.screen, self.colors["split_line"], rect, 1)
        self._draw_tree_borders(node.left)
        self._draw_tree_borders(node.right)

    def _draw_ui(self) -> None:
        """Отрисовывает текстовую панель состояния."""
        status = f"Phase: {self.phase.upper()} | Level: {self.current_level}/{self.split_depth}"
        controls = "SPACE: Step | R: Reset | Q: Quit"
        
        self.screen.blit(self.font.render(status, True, self.colors["text"]), (OFFSET_X, OFFSET_Y))
        self.screen.blit(self.font.render(controls, True, self.colors["text"]), (OFFSET_X, OFFSET_Y + 25))

    def run(self) -> None:
        """Основной цикл визуализации."""
        running = True
        while running:
            # 1. Обработка событий
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self._handle_manual_step()
                    elif event.key == pygame.K_r:
                        self.reset()
                    elif event.key == pygame.K_q:
                        running = False

            # 2. Автоматическое продвижение по фазам
            self.frame_counter += 1
            if self.frame_counter >= FRAMES_PER_STEP and self.phase != "done":
                self._handle_auto_step()
                self.frame_counter = 0

            # 3. Рендеринг
            self._render()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

    def _handle_manual_step(self) -> None:
        """Обработка одного шага по нажатию SPACE."""
        if self.phase == "partition":
            self._advance_partition()
        elif self.phase == "rooms":
            self._generate_rooms()
        elif self.phase == "corridors":
            self._generate_corridors()

    def _handle_auto_step(self) -> None:
        """Автоматический переход между фазами."""
        self._handle_manual_step()

    def _render(self) -> None:
        self.screen.fill(self.colors["bg"])
        
        # 1. Линии разбиения (рисуем только если у узла НЕТ комнаты)
        self._draw_tree_borders(self.root)
        
        # 2. Комнаты (рисуем поверх линий для читаемости)
        for rect in self.rooms:
            pygame.draw.rect(self.screen, self.colors["room_fill"], rect)
            pygame.draw.rect(self.screen, self.colors["room_border"], rect, 2)
            
        # 3. Коридоры
        for c in self.corridors:
            pygame.draw.line(self.screen, self.colors["corridor"], (c[0], c[1]), (c[2], c[3]), 4)
            
        self._draw_ui()


if __name__ == "__main__":
    viz = BSPVisualizer(split_depth=5)
    viz.run()