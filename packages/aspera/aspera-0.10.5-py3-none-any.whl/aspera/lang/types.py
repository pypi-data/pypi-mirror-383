"""
ASPERA Type System
==================
Union types, type inference, and compile-time validation.

Author: Christian Quintino De Luca - RTH Italia
Version: 0.1.0
"""

from typing import Any, Dict, List, Optional, Set, Union as TypingUnion
from enum import Enum


class BaseType(Enum):
    """Base types in ASPERA"""
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"
    ANY = "any"
    VOID = "void"


class AsperaType:
    """Type representation supporting union types"""
    
    def __init__(self, types: TypingUnion[BaseType, List[BaseType]]):
        if isinstance(types, BaseType):
            self.types = {types}
        elif isinstance(types, list):
            self.types = set(types)
        else:
            self.types = {types}
    
    def is_union(self) -> bool:
        return len(self.types) > 1
    
    def includes(self, other_type: BaseType) -> bool:
        return other_type in self.types or BaseType.ANY in self.types
    
    def is_compatible(self, other: 'AsperaType') -> bool:
        """Check if this type is compatible with another"""
        if BaseType.ANY in self.types or BaseType.ANY in other.types:
            return True
        return bool(self.types & other.types)
    
    def __str__(self) -> str:
        if len(self.types) == 1:
            return list(self.types)[0].value
        return " | ".join(sorted(t.value for t in self.types))
    
    def __repr__(self) -> str:
        return f"AsperaType({self})"


class TypeChecker:
    """Type checker for ASPERA AST"""
    
    def __init__(self):
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
        self.symbol_table: Dict[str, AsperaType] = {}
    
    def check_ast(self, ast: Dict[str, Any]) -> bool:
        """
        Type check entire AST.
        
        Returns:
            True if no errors, False otherwise
        """
        self.errors = []
        self.warnings = []
        self.symbol_table = {}
        
        for node in ast.get("nodes", []):
            self._check_node(node)
        
        return len(self.errors) == 0
    
    def _check_node(self, node: Dict[str, Any]):
        """Check a single node"""
        node_type = node.get("type")
        
        if node_type == "concept":
            self._check_concept(node)
        elif node_type == "state":
            self._check_state(node)
        elif node_type == "inference":
            self._check_inference(node)
        elif node_type == "intention":
            self._check_intention(node)
    
    def _check_concept(self, node: Dict[str, Any]):
        """Type check concept node"""
        name = node.get("name")
        baseline = node.get("baseline", 0.5)
        decay_rate = node.get("decay_rate", 0.05)
        
        # Register concept as number type
        self.symbol_table[f"concept.{name}"] = AsperaType(BaseType.NUMBER)
        
        # Validate baseline
        if not isinstance(baseline, (int, float)) or not (0 <= baseline <= 1):
            self.errors.append({
                "type": "TypeError",
                "message": f"Concept '{name}' baseline must be number between 0 and 1, got {baseline}",
                "node": name
            })
        
        # Validate decay_rate
        if not isinstance(decay_rate, (int, float)) or not (0 <= decay_rate <= 1):
            self.errors.append({
                "type": "TypeError",
                "message": f"Concept '{name}' decay_rate must be number between 0 and 1, got {decay_rate}",
                "node": name
            })
    
    def _check_state(self, node: Dict[str, Any]):
        """Type check state node"""
        entries = node.get("entries", {})
        
        for key, value in entries.items():
            # Infer type from value
            inferred_type = self._infer_type(value)
            self.symbol_table[f"state.{key}"] = inferred_type
    
    def _check_inference(self, node: Dict[str, Any]):
        """Type check inference node"""
        when_ast = node.get("when_ast")
        then_action = node.get("then_action")
        
        if when_ast:
            self._check_expression(when_ast)
        
        if then_action:
            self._check_action(then_action, node.get("name", "unknown"))
    
    def _check_intention(self, node: Dict[str, Any]):
        """Type check intention node"""
        strategy = node.get("strategy", [])
        
        for rule in strategy:
            if "condition" in rule:
                self._check_expression(rule["condition"])
    
    def _check_expression(self, expr: Dict[str, Any]) -> Optional[AsperaType]:
        """
        Type check expression and return its type.
        
        Returns:
            AsperaType or None if error
        """
        expr_type = expr.get("expr_type")
        
        if expr_type == "literal":
            value_type = expr.get("value_type")
            if value_type == "number":
                return AsperaType(BaseType.NUMBER)
            elif value_type == "string":
                return AsperaType(BaseType.STRING)
            elif value_type == "boolean":
                return AsperaType(BaseType.BOOLEAN)
        
        elif expr_type == "identifier":
            path = expr.get("path", [])
            symbol_name = ".".join(path)
            
            if symbol_name in self.symbol_table:
                return self.symbol_table[symbol_name]
            else:
                # Try to infer from context
                if path and path[0] in ["signals", "state", "concept"]:
                    return AsperaType(BaseType.NUMBER)  # Default assumption
        
        elif expr_type == "binary_op":
            operator = expr.get("operator")
            left_type = self._check_expression(expr.get("left", {}))
            right_type = self._check_expression(expr.get("right", {}))
            
            # Comparison operators always return boolean
            if operator in [">", "<", ">=", "<=", "==", "!=", "and", "or"]:
                return AsperaType(BaseType.BOOLEAN)
            
            # Arithmetic operators return number
            elif operator in ["+", "-", "*", "/", "%"]:
                if left_type and right_type:
                    if not left_type.includes(BaseType.NUMBER) or not right_type.includes(BaseType.NUMBER):
                        self.errors.append({
                            "type": "TypeError",
                            "message": f"Operator '{operator}' requires numeric operands",
                            "left_type": str(left_type),
                            "right_type": str(right_type)
                        })
                return AsperaType(BaseType.NUMBER)
        
        return AsperaType(BaseType.ANY)
    
    def _check_action(self, action: Dict[str, Any], inference_name: str):
        """Type check action"""
        action_type = action.get("action_type")
        
        if action_type in ["increase", "decrease"]:
            concept = action.get("concept")
            delta = action.get("delta", 0)
            
            # Check delta is number
            if not isinstance(delta, (int, float)):
                self.errors.append({
                    "type": "TypeError",
                    "message": f"Inference '{inference_name}': delta must be number, got {type(delta).__name__}",
                    "concept": concept
                })
            
            # Check delta in valid range
            if not (0 <= abs(delta) <= 1):
                self.warnings.append({
                    "type": "TypeWarning",
                    "message": f"Inference '{inference_name}': delta {delta} outside typical range [0, 1]",
                    "concept": concept
                })
    
    def _infer_type(self, value: Any) -> AsperaType:
        """Infer ASPERA type from Python value"""
        if isinstance(value, bool):
            return AsperaType(BaseType.BOOLEAN)
        elif isinstance(value, (int, float)):
            return AsperaType(BaseType.NUMBER)
        elif isinstance(value, str):
            return AsperaType(BaseType.STRING)
        elif isinstance(value, list):
            return AsperaType(BaseType.ARRAY)
        elif isinstance(value, dict):
            return AsperaType(BaseType.OBJECT)
        else:
            return AsperaType(BaseType.ANY)
    
    def get_report(self) -> Dict[str, Any]:
        """Get type checking report"""
        return {
            "errors": self.errors,
            "warnings": self.warnings,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "symbols": {name: str(type_) for name, type_ in self.symbol_table.items()}
        }


def type_check(ast: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to type check an AST.
    
    Args:
        ast: ASPERA AST dictionary
    
    Returns:
        Type check report dictionary
    
    Example:
        >>> report = type_check(ast)
        >>> if report["error_count"] > 0:
        ...     print(f"Found {report['error_count']} type errors")
    """
    checker = TypeChecker()
    checker.check_ast(ast)
    return checker.get_report()

