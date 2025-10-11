"""
ASPERA Symbolic Reasoner
=========================
Esegue inferenze deterministiche basate su regole simboliche.
Valuta espressioni logiche e applica azioni al contesto.

Author: Christian Quintino De Luca - RTH Italia
"""

from typing import Any, Dict, List, Optional, Tuple
import logging
from copy import deepcopy
from aspera.runtime.thresholds import get_thresholds

logger = logging.getLogger(__name__)


class SymbolicReasoner:
    """
    Reasoner simbolico per ASPERA.
    Valuta espressioni AST e applica inferenze deterministiche.
    """

    def __init__(self):
        self.context: Dict[str, Any] = {
            "signals": {},
            "concept": {},
            "state": {},
            "experiences": {}
        }
        self.audit_log: List[Dict[str, Any]] = []

    def load_context(self, signals: Dict[str, Any], state: Dict[str, Any],
                     concepts: Dict[str, float], experiences: Dict[str, Any] = None):
        """
        Carica il contesto di esecuzione.

        Args:
            signals: Segnali di input
            state: Stato corrente del sistema
            concepts: Valori baseline dei concetti
            experiences: Esperienze accumulate (opzionale)
        """
        self.context = {
            "signals": signals or {},
            "concept": concepts or {},
            "state": state or {},
            "experiences": experiences or {}
        }
        logger.debug(f"Context loaded: {self.context}")

    def evaluate_expression(self, expr_ast: Dict[str, Any]) -> Any:
        """
        Valuta un'espressione AST.

        Args:
            expr_ast: Nodo espressione AST

        Returns:
            Valore dell'espressione valutata
        """
        expr_type = expr_ast.get("expr_type")

        if expr_type == "literal":
            return expr_ast["value"]

        elif expr_type == "identifier":
            path = expr_ast["path"]
            return self._resolve_path(path)

        elif expr_type == "binary_op":
            operator = expr_ast["operator"]
            left = self.evaluate_expression(expr_ast["left"])
            right = self.evaluate_expression(expr_ast["right"])
            return self._apply_binary_op(operator, left, right)

        elif expr_type == "unary_op":
            operator = expr_ast["operator"]
            operand = self.evaluate_expression(expr_ast["operand"])
            return self._apply_unary_op(operator, operand)

        elif expr_type == "function_call":
            func_name = expr_ast["function_name"]
            args = [self.evaluate_expression(arg) for arg in expr_ast["arguments"]]
            return self._call_function(func_name, args)

        else:
            raise ValueError(f"Unknown expression type: {expr_type}")

    def _resolve_path(self, path: List[str]) -> Any:
        """Risolve un percorso dotted nel contesto"""
        current = self.context
        for part in path:
            if isinstance(current, dict):
                if part not in current:
                    logger.debug(f"Path component '{part}' not found in context")
                    return 0.0  # Default per valori mancanti
                current = current[part]
            else:
                logger.warning(f"Cannot traverse path {path}, stopped at {part}")
                return 0.0
        return current

    def _apply_binary_op(self, operator: str, left: Any, right: Any) -> Any:
        """Applica operatore binario"""
        ops = {
            "+": lambda l, r: l + r,
            "-": lambda l, r: l - r,
            "*": lambda l, r: l * r,
            "/": lambda l, r: l / r if r != 0 else float('inf'),
            "%": lambda l, r: l % r if r != 0 else 0,
            ">": lambda l, r: l > r,
            "<": lambda l, r: l < r,
            ">=": lambda l, r: l >= r,
            "<=": lambda l, r: l <= r,
            "==": lambda l, r: l == r,
            "!=": lambda l, r: l != r,
            "and": lambda l, r: l and r,
            "or": lambda l, r: l or r,
        }
        if operator not in ops:
            raise ValueError(f"Unknown binary operator: {operator}")
        return ops[operator](left, right)

    def _apply_unary_op(self, operator: str, operand: Any) -> Any:
        """Applica operatore unario"""
        if operator == "not":
            return not operand
        elif operator == "-":
            return -operand
        else:
            raise ValueError(f"Unknown unary operator: {operator}")

    def _call_function(self, func_name: str, args: List[Any]) -> Any:
        """Chiama funzione built-in"""
        builtins = {
            "abs": lambda x: abs(x[0]) if x else 0,
            "min": lambda x: min(x) if x else 0,
            "max": lambda x: max(x) if x else 0,
            "len": lambda x: len(x[0]) if x and hasattr(x[0], '__len__') else 0,
            # Recupera/propone soglia adattiva da registro globale
            "threshold": lambda x: get_thresholds().get_value(
                str(x[0]) if x else "",
                float(x[1]) if len(x) > 1 else 0.5,
            ),
        }
        if func_name in builtins:
            return builtins[func_name](args)
        else:
            logger.warning(f"Unknown function: {func_name}")
            return 0

    def apply_inference(self, inference_node: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Applica una regola di inferenza.

        Args:
            inference_node: Nodo inferenza dall'AST

        Returns:
            Risultato dell'applicazione (o None se condizione non soddisfatta)
        """
        inference_id = inference_node["id"]
        inference_name = inference_node["name"]
        when_ast = inference_node["when_ast"]
        then_action = inference_node["then_action"]
        confidence = inference_node.get("confidence", 1.0)
        mode = inference_node.get("mode", "symbolic")

        # Valuta condizione
        try:
            condition_result = self.evaluate_expression(when_ast)
        except Exception as e:
            logger.error(f"Error evaluating condition for {inference_name}: {e}")
            condition_result = False

        if not condition_result:
            return None

        # Condizione soddisfatta, applica azione
        logger.info(f"Inference '{inference_name}' triggered (confidence: {confidence})")

        result = {
            "inference_id": inference_id,
            "inference_name": inference_name,
            "confidence": confidence,
            "mode": mode,
            "action": then_action,
            "changes": []
        }

        # Applica azione
        changes = self._apply_action(then_action)
        result["changes"] = changes

        # Aggiungi al log di audit
        self.audit_log.append({
            "type": "inference",
            "inference": inference_name,
            "condition_met": True,
            "confidence": confidence,
            "changes": changes,
            "context_snapshot": deepcopy(self.context)
        })

        return result

    def _apply_action(self, action_node: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Applica un'azione al contesto"""
        action_type = action_node["action_type"]
        changes = []

        if action_type == "increase":
            concept_name = action_node["concept"]
            delta = action_node["delta"]
            if concept_name in self.context["concept"]:
                old_value = self.context["concept"][concept_name]
                new_value = min(1.0, old_value + delta)  # Cap at 1.0
                self.context["concept"][concept_name] = new_value
                changes.append({
                    "type": "concept_change",
                    "concept": concept_name,
                    "old_value": old_value,
                    "new_value": new_value,
                    "delta": delta
                })
                logger.debug(f"Increased concept '{concept_name}': {old_value} -> {new_value}")
            else:
                logger.warning(f"Concept '{concept_name}' not found in context")

        elif action_type == "decrease":
            concept_name = action_node["concept"]
            delta = action_node["delta"]
            if concept_name in self.context["concept"]:
                old_value = self.context["concept"][concept_name]
                new_value = max(0.0, old_value - delta)  # Floor at 0.0
                self.context["concept"][concept_name] = new_value
                changes.append({
                    "type": "concept_change",
                    "concept": concept_name,
                    "old_value": old_value,
                    "new_value": new_value,
                    "delta": -delta
                })
                logger.debug(f"Decreased concept '{concept_name}': {old_value} -> {new_value}")
            else:
                logger.warning(f"Concept '{concept_name}' not found in context")

        elif action_type == "set":
            target = action_node["target"]
            value = action_node["value"]
            self._set_value(target, value)
            changes.append({
                "type": "state_change",
                "target": ".".join(target),
                "value": value
            })
            logger.debug(f"Set {'.'.join(target)} = {value}")

        elif action_type == "say":
            message = action_node["message"]
            changes.append({
                "type": "output",
                "message": message
            })
            logger.info(f"Say: {message}")

        elif action_type == "trigger":
            event_name = action_node["event_name"]
            data = action_node.get("data", {})
            changes.append({
                "type": "event",
                "event": event_name,
                "data": data
            })
            logger.info(f"Triggered event: {event_name}")

        elif action_type == "multi":
            for sub_action in action_node["actions"]:
                changes.extend(self._apply_action(sub_action))

        return changes

    def _set_value(self, path: List[str], value: Any):
        """Imposta un valore nel contesto seguendo un percorso"""
        current = self.context
        for part in path[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[path[-1]] = value

    def get_context(self) -> Dict[str, Any]:
        """Ritorna il contesto corrente"""
        return deepcopy(self.context)

    def get_audit_log(self) -> List[Dict[str, Any]]:
        """Ritorna il log di audit"""
        return deepcopy(self.audit_log)

    def clear_audit_log(self):
        """Pulisce il log di audit"""
        self.audit_log = []

