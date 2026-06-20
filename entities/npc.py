import math
from enum import Enum
from typing import Tuple, Optional
import pygame

from ai import (
    Blackboard,
    BTNode,
    Sequence,
    Selector,
    Condition,
    Action,
    NodeStatus,
    MarkovChain
)
from config.display_config import FPS
from config.gameplay_config import (
    NPC_MAX_HEALTH,
    NPC_SPEED,
    NPC_DELTA_TIME,
    NPC_LABEL_FONT_SIZE,
    NPC_PATROL_ANGLE,
    NPC_RADIUS,
    PATROL_ANGLE_DELTA,
    POS_DELTA,
    LOOT_REWARDS,
    OXYGEN_DRAIN_PER_SECOND
)
from config.content_config import (
    LORE_CONTEXT_START,
    LORE_TEXT_LENGTH,
    LORE_VOCABULARY,
    GAME_TRANSITIONS,
)
from config.logging_config import setup_logger
from loot.weighted_binary import WeightedBinaryLootGenerator as WBLGen


logger = setup_logger(__name__)

class NPCType(Enum):
    ATTACKER = "attacker"
    ESCAPER = "escaper"
    STORYTELLER = "storyteller"


class NPC:
    """Игровой NPC. Использует BT для логики и цепь Маркова для нарратива."""

    def __init__(
        self,
        npc_id: str,
        start_pos: Tuple[float, float],
        bt_root: BTNode,
        lore_chain: MarkovChain,
        npc_type: NPCType = NPCType.ATTACKER,
        dialog_rewards: Optional[WBLGen] = None, 
    ):
        self.id = npc_id
        self.position = start_pos
        self.npc_type = npc_type
        self.speed = NPC_SPEED
        self.radius = NPC_RADIUS
        self.rect = pygame.Rect(
            int(start_pos[0] - self.radius),
            int(start_pos[1] - self.radius),
            self.radius * 2,
            self.radius * 2,
        )
        self.patrol_center = start_pos
        self._patrol_angle = NPC_PATROL_ANGLE
        self.blackboard = Blackboard()
        self.bt_root = bt_root
        self.lore_chain = lore_chain
        self._setup_blackboard()
        self.lore = self.speak_lore()

        if dialog_rewards is not None:
            self.dialog_rewards = dialog_rewards
        elif npc_type == NPCType.STORYTELLER:
            self.dialog_rewards = WBLGen(LOOT_REWARDS)
        else:
            self.dialog_rewards = None
    
        logger.info(
        f"Инициализирован NPC {self.id}, тип {self.npc_type.value}, "
        f"координата {self.position}"
        )

    def _setup_blackboard(self) -> None:
        """Создание доски с характеристиками NPC и их
        маркерами поведения.
        """
        self.blackboard.set("position", self.position)
        self.blackboard.set("health", NPC_MAX_HEALTH)
        self.blackboard.set("sees_player", False)
        self.blackboard.set("action_log", [])

    def update(self, delta_time: float = NPC_DELTA_TIME) -> None:
        """Основной тик ИИ."""
        status = self.bt_root.tick(self.blackboard)

        # Реакция на статус выполнения
        if status == NodeStatus.SUCCESS:
            self._on_cycle_complete()
        elif status == NodeStatus.FAILURE:
            self._on_cycle_interrupted()

    def speak_lore(self, context: str = LORE_CONTEXT_START) -> str:
        """Генерация текста через цепь Маркова.
        
        Attributes:
            context: Токен начала текста.

        Returns:
            text: Сгенерированный лор.
        """
        raw_tokens = self.lore_chain.generate(context, LORE_TEXT_LENGTH)
        
        cleaned_tokens = [raw_tokens[0]] if raw_tokens else []
        for i in range(1, len(raw_tokens)):
            if raw_tokens[i] != raw_tokens[i-1]:
                cleaned_tokens.append(raw_tokens[i])

        phrases = []
        for token in cleaned_tokens:
            phrase = LORE_VOCABULARY.get(token, f"[{token.upper()}]")
            phrases.append(phrase)
        
        text = " ".join(phrases)
        
        logger.info("Сгенерирован лорный элемент")
        return text
    
    def generate_dialog_reward(self) -> Optional[str]:
        """
        Генерирует награду за диалог через взвешенный бинарный поиск.
        Возвращает тип награды или None, если у NPC нет сундучка.
        """
        if self.dialog_rewards is None:
            return None
        return self.dialog_rewards.draw()

    def talk(self) -> Tuple[str, Optional[str]]:
        """
        Комплексное взаимодействие: генерирует лор + награду.
        Возвращает кортеж (текст_истории, тип_награды).
        """
        lore_text = self.speak_lore()
        reward = self.generate_dialog_reward()
        return lore_text, reward

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовка объекта NPC"""
        color_map = {
            NPCType.ATTACKER: (220, 80, 80),
            NPCType.ESCAPER: (80, 180, 220),
            NPCType.STORYTELLER: (190, 190, 90),
        }
        npc_color = color_map.get(self.npc_type, (220, 80, 80))
        pygame.draw.circle(surface, npc_color, self.rect.center, self.radius)

        label = pygame.font.Font(None, NPC_LABEL_FONT_SIZE).render(
            self.id, True, (235, 235, 235)
        )
        surface.blit(
            label, (self.rect.centerx - label.get_width() // 2, self.rect.top - 18)
        )
        if self.npc_type == NPCType.STORYTELLER:
            mark = pygame.font.Font(None, 18).render("?", True, (255, 255, 255))
            surface.blit(
                mark,
                (self.rect.centerx - mark.get_width() // 2, self.rect.centery - mark.get_height() // 2),
            )

    def move_to(
        self, target: Tuple[float, float], max_step: float | None = None
    ) -> None:
        """Движение в сторону цели

        Attributes:
            target: Объект направления движения
            max_step: Максимальный шаг NPC
        """
        dx = target[0] - self.position[0]
        dy = target[1] - self.position[1]
        distance = math.hypot(dx, dy)
        if distance < 1e-3:
            return
        step = min(max_step if max_step is not None else self.speed, distance)
        self.position = (
            self.position[0] + dx / distance * step,
            self.position[1] + dy / distance * step,
        )
        self.rect.center = (int(self.position[0]), int(self.position[1]))
        self.blackboard.set("position", self.position)

    def patrol(self) -> None:
        """Патрулирование: вращение по кругу"""
        self._patrol_angle += PATROL_ANGLE_DELTA
        self.position = (
            self.patrol_center[0] + math.cos(self._patrol_angle) * POS_DELTA,
            self.patrol_center[1] + math.sin(self._patrol_angle) * POS_DELTA,
        )
        self.rect.center = (int(self.position[0]), int(self.position[1]))
        self.blackboard.set("position", self.position)

    def _on_cycle_complete(self) -> None:
        """Фиксация успешного цикла патруля"""
        self.blackboard.set(
            "action_log", self.blackboard.get("action_log") + ["patrol_done"]
        )

    def _on_cycle_interrupted(self) -> None:
        "Цикл патруля прерван"
        self.blackboard.set(
            "action_log", self.blackboard.get("action_log") + ["reset_behavior"]
        )
        logger.info(f"Патруль {self.id} остановлен, смена поведения")

    def apply_player_effect(self, player) -> float:
        """Возвращает дополнительное ослабление игрока при контакте с NPC."""
        if self.npc_type == NPCType.ATTACKER and self.rect.colliderect(player.rect):
            return 2 * OXYGEN_DRAIN_PER_SECOND / FPS
        return 0.0

    def __repr__(self) -> str:
        return f"NPC(ID:{self.id}, TYPE:{self.npc_type.value})"


if __name__ == "__main__":
    # 1. Конфигурация цепи Маркова
    lore_transitions = GAME_TRANSITIONS
    lore_chain = MarkovChain(lore_transitions)

    # 2. Сборка дерева поведения
    def check_sees_player(bb: Blackboard) -> bool:
        return bb.get("sees_player") is True

    def move_to_patrol(bb: Blackboard) -> NodeStatus:
        # Имитация действия: обновляет позицию, пишет в лог
        bb.set("action_log", bb.get("action_log") + ["patrolling"])
        return NodeStatus.SUCCESS

    def chase_player(bb: Blackboard) -> NodeStatus:
        bb.set("action_log", bb.get("action_log") + ["chasing"])
        return NodeStatus.RUNNING  # Может занять несколько кадров

    root_bt = Selector(
        [
            Sequence([Condition(check_sees_player), Action(chase_player)]),
            Action(move_to_patrol),
        ]
    )

    # 3. Создание NPC
    npc = NPC(
        npc_id="deep_drone_01",
        start_pos=(10.0, -5.0),
        bt_root=root_bt,
        lore_chain=lore_chain,
    )

    # 4. Демонстрация работы
    print("Лор:", npc.speak_lore())
    npc.update(delta_time=NPC_DELTA_TIME)
    print("Лог действий:", npc.blackboard.get("action_log"))
