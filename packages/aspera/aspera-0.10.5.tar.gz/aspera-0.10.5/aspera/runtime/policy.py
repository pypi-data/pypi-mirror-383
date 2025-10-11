"""
ASPERA Policy Executor
======================
Esegue strategie delle intention nodes per selezionare azioni di alto livello.

Author: Christian Quintino De Luca - RTH Italia
"""

from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class PolicyExecutor:
    """
    Esegue policy strategiche definite nei nodi intention.
    Valuta strategie condizionali e seleziona azioni appropriate.
    """

    def __init__(self, symbolic_reasoner=None):
        self.symbolic_reasoner = symbolic_reasoner
        self.action_history: List[Dict[str, Any]] = []

    def execute_intention(self, intention_node: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Esegue una intention strategy.

        Args:
            intention_node: Nodo intention dall'AST

        Returns:
            Azione selezionata con metadati
        """
        intention_id = intention_node["id"]
        intention_name = intention_node["name"]
        priority = intention_node.get("priority", "medium")
        goal = intention_node.get("goal", "")
        strategies = intention_node.get("strategy", [])
        timeout = intention_node.get("timeout")

        logger.info(f"Executing intention: {intention_name} (priority: {priority})")

        # Valuta strategie in ordine
        selected_action = None
        matched_rule = None

        for strategy_rule in strategies:
            rule_type = strategy_rule["rule_type"]

            if rule_type == "always":
                # Always rules hanno precedenza
                selected_action = strategy_rule["action"]
                matched_rule = strategy_rule
                logger.debug(f"Matched 'always' rule: {selected_action}")
                break

            elif rule_type == "if":
                # Valuta condizione
                condition = strategy_rule.get("condition")
                if condition and self.symbolic_reasoner:
                    try:
                        condition_met = self.symbolic_reasoner.evaluate_expression(condition)
                        if condition_met:
                            selected_action = strategy_rule["action"]
                            matched_rule = strategy_rule
                            logger.debug(f"Matched 'if' rule: {selected_action}")
                            break
                    except Exception as e:
                        logger.error(f"Error evaluating strategy condition: {e}")
                        continue

            elif rule_type == "else":
                # Else è fallback se nessuna if è stata matchata
                if selected_action is None:
                    selected_action = strategy_rule["action"]
                    matched_rule = strategy_rule
                    logger.debug(f"Matched 'else' rule: {selected_action}")

        if selected_action is None:
            logger.warning(f"No action selected for intention: {intention_name}")
            return None

        # Costruisci risultato
        result = {
            "intention_id": intention_id,
            "intention_name": intention_name,
            "priority": priority,
            "goal": goal,
            "action": selected_action,
            "matched_rule": matched_rule,
            "timeout": timeout
        }

        # Aggiungi alla storia
        self.action_history.append(result)

        return result

    def execute_all_intentions(self, intentions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Esegue tutte le intention in ordine di priorità.

        Args:
            intentions: Lista di nodi intention

        Returns:
            Lista di azioni selezionate
        """
        # Ordina per priorità
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        sorted_intentions = sorted(
            intentions,
            key=lambda i: priority_order.get(i.get("priority", "medium"), 2)
        )

        actions = []
        for intention in sorted_intentions:
            result = self.execute_intention(intention)
            if result:
                actions.append(result)

        return actions

    def get_action_history(self) -> List[Dict[str, Any]]:
        """Ritorna la storia delle azioni selezionate"""
        return self.action_history

    def clear_history(self):
        """Pulisce la storia"""
        self.action_history = []

