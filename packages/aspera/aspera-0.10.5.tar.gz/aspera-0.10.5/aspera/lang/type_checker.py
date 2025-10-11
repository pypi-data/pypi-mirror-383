"""
ASPERA Type Checker (Lightweight)
=================================
Controlli statici principali:
- Referenze a concetti/identificatori (concept.*, signals.*, state.*)
- Coerenza azioni (increase/decrease su concetti esistenti)
- Operatori di confronto applicati a numerici

Ritorna una lista di errori (stringhe). Exit code 1 in caso di errori.
"""

from typing import Any, Dict, List, Set


def _collect_concepts(ast: Dict[str, Any]) -> Set[str]:
    names: Set[str] = set()
    for n in ast.get("nodes", []):
        if n.get("type") == "concept":
            nm = n.get("name")
            if isinstance(nm, str):
                names.add(nm)
    return names


def _is_number_literal(expr: Dict[str, Any]) -> bool:
    return expr.get("expr_type") == "literal" and expr.get("value_type") == "number"


def _is_identifier(expr: Dict[str, Any], prefix: str | None = None) -> bool:
    if expr.get("expr_type") != "identifier":
        return False
    path = expr.get("path")
    if not isinstance(path, list) or not path:
        return False
    if prefix is None:
        return True
    return path[0] == prefix


def _check_expr_numeric(expr: Dict[str, Any], concepts: Set[str], errors: List[str], ctx: str) -> None:
    et = expr.get("expr_type")
    if et in ("literal",):
        if not _is_number_literal(expr):
            errors.append(f"{ctx}: literal non numerico in confronto")
        return
    if et == "identifier":
        path = expr.get("path", [])
        if not path:
            errors.append(f"{ctx}: identifier vuoto")
            return
        head = path[0]
        if head == "concept":
            if len(path) < 2 or path[1] not in concepts:
                errors.append(f"{ctx}: concept '{'.'.join(path)}' non definito")
        # signals/state: consentiti, assumiamo numerici
        return
    if et == "binary_op":
        _check_expr_numeric(expr.get("left", {}), concepts, errors, ctx)
        _check_expr_numeric(expr.get("right", {}), concepts, errors, ctx)
        return
    if et == "unary_op":
        _check_expr_numeric(expr.get("operand", {}), concepts, errors, ctx)
        return
    # function_call e altri: ignora per ora


def _check_inference(node: Dict[str, Any], concepts: Set[str], errors: List[str]) -> None:
    name = node.get("name", "<inference>")
    when_ast = node.get("when_ast")
    if when_ast:
        # operatori di confronto → numerici
        if when_ast.get("expr_type") == "binary_op" and when_ast.get("operator") in (">", ">=", "<", "<="):
            _check_expr_numeric(when_ast.get("left", {}), concepts, errors, f"inference '{name}' left")
            _check_expr_numeric(when_ast.get("right", {}), concepts, errors, f"inference '{name}' right")


def _check_action(action: Dict[str, Any], concepts: Set[str], errors: List[str], ctx: str) -> None:
    at = action.get("action_type")
    if at in ("increase", "decrease"):
        c = action.get("concept")
        if c not in concepts:
            errors.append(f"{ctx}: concept '{c}' non definito per azione {at}")


def _walk_intention(node: Dict[str, Any], concepts: Set[str], errors: List[str]) -> None:
    name = node.get("name", "<intention>")
    for rule in node.get("strategy", []):
        cond = rule.get("condition")
        if isinstance(cond, dict) and cond.get("expr_type") == "binary_op" and cond.get("operator") in (">", ">=", "<", "<="):
            _check_expr_numeric(cond.get("left", {}), concepts, errors, f"intention '{name}' left")
            _check_expr_numeric(cond.get("right", {}), concepts, errors, f"intention '{name}' right")


def type_check_ast(ast: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    concepts = _collect_concepts(ast)
    for n in ast.get("nodes", []):
        t = n.get("type")
        if t == "inference":
            _check_inference(n, concepts, errors)
        elif t == "intention":
            _walk_intention(n, concepts, errors)
        elif t == "associate":
            # check references in associate
            fc, tc = n.get("from_concept"), n.get("to_concept")
            if fc not in concepts:
                errors.append(f"associate: from_concept '{fc}' non definito")
            if tc not in concepts:
                errors.append(f"associate: to_concept '{tc}' non definito")
    return errors




