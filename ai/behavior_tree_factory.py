"""Фабрика поведенческих деревьев для NPC."""
import math
import ai
from entities.npc import NPC, NPCType


class NPCBehaviorTreeFactory:
    """Создаёт поведенческие деревья для разных типов NPC."""
    
    def create_behavior_tree(self, npc: NPC) -> ai.BTNode:
        """
        Создаёт поведение для NPC в зависимости от типа.
        
        Args:
            npc: NPC, для которого создаётся дерево
            
        Returns:
            Корневой узел поведенческого дерева
        """
        if npc.npc_type == NPCType.ATTACKER:
            return self._create_attacker_tree()
        elif npc.npc_type == NPCType.ESCAPER:
            return self._create_escaper_tree()
        elif npc.npc_type == NPCType.STORYTELLER:
            return self._create_storyteller_tree()
        else:
            # Поведение по умолчанию
            return ai.Action(lambda bb: ai.NodeStatus.SUCCESS)
    
    def _create_attacker_tree(self) -> ai.BTNode:
        """Поведение атакующего: преследует игрока или патрулирует."""
        return ai.Selector([
            ai.Sequence([
                ai.Condition(self._check_sees_player),
                ai.Action(self._move_toward_player),
            ]),
            ai.Action(self._patrol_action),
        ])
    
    def _create_escaper_tree(self) -> ai.BTNode:
        """Поведение убегающего: убегает от игрока или патрулирует."""
        return ai.Selector([
            ai.Sequence([
                ai.Condition(self._check_sees_player),
                ai.Action(self._move_away_from_player),
            ]),
            ai.Action(self._patrol_action),
        ])
    
    def _create_storyteller_tree(self) -> ai.BTNode:
        """Поведение рассказчика: стоит на месте."""
        return ai.Selector([
            ai.Action(self._storyteller_idle),
        ])
    
    @staticmethod
    def _check_sees_player(bb: ai.Blackboard) -> bool:
        """Проверяет, видит ли NPC игрока."""
        return bb.get("sees_player") is True
    
    @staticmethod
    def _move_toward_player(bb: ai.Blackboard) -> ai.NodeStatus:
        """Двигается к игроку."""
        npc = bb.get("npc")
        player = bb.get("player")
        
        if not player:
            return ai.NodeStatus.FAILURE
        
        npc.move_to(player.rect.center, max_step=npc.speed)
        return ai.NodeStatus.RUNNING
    
    @staticmethod
    def _move_away_from_player(bb: ai.Blackboard) -> ai.NodeStatus:
        """Убегает от игрока."""
        npc = bb.get("npc")
        player = bb.get("player")
        
        if not player:
            return ai.NodeStatus.FAILURE
        
        dx = npc.position[0] - player.rect.centerx
        dy = npc.position[1] - player.rect.centery
        distance = math.hypot(dx, dy)
        
        if distance < 1e-3:
            return ai.NodeStatus.FAILURE
        
        target = (
            npc.position[0] + dx / distance * npc.speed * 1.2,
            npc.position[1] + dy / distance * npc.speed * 1.2,
        )
        npc.move_to(target, max_step=npc.speed)
        return ai.NodeStatus.RUNNING
    
    @staticmethod
    def _patrol_action(bb: ai.Blackboard) -> ai.NodeStatus:
        """Патрулирует территорию."""
        npc = bb.get("npc")
        npc.patrol()
        return ai.NodeStatus.SUCCESS
    
    @staticmethod
    def _storyteller_idle(bb: ai.Blackboard) -> ai.NodeStatus:
        """Стоит на месте."""
        return ai.NodeStatus.SUCCESS