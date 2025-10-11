"""
ASPERA SDK Utilities
====================
Utility functions per SDK.

Author: Christian Quintino De Luca - RTH Italia
"""

import json
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)


def pretty_print_ast(ast: Dict[str, Any]) -> str:
    """
    Formatta AST in modo leggibile.

    Args:
        ast: AST dictionary

    Returns:
        Stringa formattata
    """
    return json.dumps(ast, indent=2, ensure_ascii=False)


def ast_to_summary(ast: Dict[str, Any]) -> Dict[str, Any]:
    """
    Crea un summary leggibile dell'AST.

    Args:
        ast: AST dictionary

    Returns:
        Summary con statistiche
    """
    nodes = ast.get("nodes", [])
    summary = {
        "version": ast.get("version"),
        "total_nodes": len(nodes),
        "concepts": [],
        "associations": [],
        "inferences": [],
        "intentions": [],
        "has_explain": False
    }

    for node in nodes:
        node_type = node.get("type")
        if node_type == "concept":
            summary["concepts"].append({
                "name": node["name"],
                "baseline": node.get("baseline", 0.5)
            })
        elif node_type == "associate":
            summary["associations"].append({
                "from": node["from_concept"],
                "to": node["to_concept"],
                "weight": node.get("weight", 0.5)
            })
        elif node_type == "inference":
            summary["inferences"].append({
                "name": node["name"],
                "priority": node.get("priority", "medium"),
                "mode": node.get("mode", "symbolic")
            })
        elif node_type == "intention":
            summary["intentions"].append({
                "name": node["name"],
                "priority": node.get("priority", "medium")
            })
        elif node_type == "explain":
            summary["has_explain"] = True

    return summary


def validate_signals(signals: Dict[str, Any], required_keys: list = None) -> bool:
    """
    Valida che signals dictionary abbia le chiavi richieste.

    Args:
        signals: Signals dictionary
        required_keys: Lista di chiavi richieste

    Returns:
        True se valido

    Raises:
        ValueError: Se validazione fallisce
    """
    if not isinstance(signals, dict):
        raise ValueError("signals must be a dictionary")

    if required_keys:
        missing = set(required_keys) - set(signals.keys())
        if missing:
            raise ValueError(f"Missing required signal keys: {missing}")

    return True


def format_explanation(explanation: str, max_length: int = None) -> str:
    """
    Formatta una spiegazione per display.

    Args:
        explanation: Testo spiegazione
        max_length: Lunghezza massima (opzionale)

    Returns:
        Spiegazione formattata
    """
    if max_length and len(explanation) > max_length:
        explanation = explanation[:max_length] + "..."

    return explanation.strip()


def compare_states(state1: Dict[str, Any], state2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Confronta due stati e ritorna differenze.

    Args:
        state1: Primo stato
        state2: Secondo stato

    Returns:
        Dictionary con differenze
    """
    differences = {
        "concepts_changed": [],
        "state_changed": []
    }

    # Confronta concepts
    concepts1 = state1.get("concepts", {})
    concepts2 = state2.get("concepts", {})

    for key in set(concepts1.keys()) | set(concepts2.keys()):
        val1 = concepts1.get(key, 0)
        val2 = concepts2.get(key, 0)
        if val1 != val2:
            differences["concepts_changed"].append({
                "concept": key,
                "before": val1,
                "after": val2,
                "delta": val2 - val1
            })

    # Confronta state
    state_entries1 = state1.get("state", {})
    state_entries2 = state2.get("state", {})

    for key in set(state_entries1.keys()) | set(state_entries2.keys()):
        val1 = state_entries1.get(key)
        val2 = state_entries2.get(key)
        if val1 != val2:
            differences["state_changed"].append({
                "key": key,
                "before": val1,
                "after": val2
            })

    return differences

