from typing import Tuple
from ai.behavior_tree import Blackboard, BTNode, Sequence, Selector, Condition, Action, NodeStatus
from ai.markov_chain import MarkovChain
from config import NPC_MAX_HEALTH, LORE_CONTEXT_START, LORE_TEXT_LENGTH

class NPC:
    """
    Агента окружения. Использует композицию: имеет BT для логики и MarkovChain для нарратива.
    Отношения: NPC -> Blackboard (ассоциация), NPC -> BT (композиция), NPC -> MarkovChain (композиция).
    """
    def __init__(self, npc_id: str, start_pos: Tuple[float, float], 
                 bt_root: BTNode, lore_chain: MarkovChain):
        self.id = npc_id
        self.position = start_pos
        self.blackboard = Blackboard()
        self.bt_root = bt_root
        self.lore_chain = lore_chain
        self._setup_blackboard()

    def _setup_blackboard(self) -> None:
        self.blackboard.set("position", self.position)
        self.blackboard.set("health", NPC_MAX_HEALTH)
        self.blackboard.set("sees_player", False)
        self.blackboard.set("action_log", [])

    def update(self, delta_time: float) -> None:
        """Основной тик ИИ. Сложность: O(d), где d — глубина дерева."""
        status = self.bt_root.tick(self.blackboard)
        
        # Реакция на статус выполнения
        if status == NodeStatus.SUCCESS:
            self._on_cycle_complete()
        elif status == NodeStatus.FAILURE:
            self._on_cycle_interrupted()

    def speak_lore(self, context: str = LORE_CONTEXT_START) -> str:
        """Генерирует атмосферный текст через цепь Маркова."""
        tokens = self.lore_chain.generate(context, LORE_TEXT_LENGTH)
        return " ".join(tokens)

    def _on_cycle_complete(self) -> None:
        self.blackboard.set("action_log", self.blackboard.get("action_log") + ["patrol_done"])

    def _on_cycle_interrupted(self) -> None:
        self.blackboard.set("action_log", self.blackboard.get("action_log") + ["reset_behavior"])

if __name__ == "__main__":
    # 1. Конфигурация цепи Маркова
    lore_transitions = {
        "submerged_lab": {"corridor": 0.6, "airlock": 0.4},
        "corridor": {"terminal": 0.7, "leak": 0.3},
        "airlock": {"pressure_chamber": 1.0},
        "terminal": {"log_entry": 0.5, "static": 0.5},
        "leak": {"alarm": 0.8, "silence": 0.2},
        "pressure_chamber": {"echo": 1.0},
        "log_entry": {"warning": 1.0},
        "static": {"static": 0.9, "log_entry": 0.1},
        "alarm": {"breach": 1.0},
        "silence": {"distant_drone": 1.0},
        "echo": {"whisper": 1.0},
        "warning": {"silence": 1.0},
        "breach": {"silence": 1.0},
        "distant_drone": {"static": 1.0},
        "whisper": {"silence": 1.0}
    }
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

    root_bt = Selector([
        Sequence([
            Condition(check_sees_player),
            Action(chase_player)
        ]),
        Action(move_to_patrol)
    ])

    # 3. Создание NPC
    npc = NPC(
        npc_id="deep_drone_01",
        start_pos=(10.0, -5.0),
        bt_root=root_bt,
        lore_chain=lore_chain
    )

    # 4. Демонстрация работы
    print("Лор:", npc.speak_lore())
    npc.update(delta_time=0.016)
    print("Лог действий:", npc.blackboard.get("action_log"))