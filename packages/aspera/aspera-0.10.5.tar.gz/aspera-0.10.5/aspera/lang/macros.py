"""
ASPERA Macro System
===================
Enables DRY (Don't Repeat Yourself) code through macro definitions and expansions.

Features:
- Define reusable macros with parameters
- Expand macros in-place during parsing
- Nested macro support
- Type-safe parameter substitution
- Macro documentation and validation

Author: Christian Quintino De Luca - RTH Italia
Version: 0.1.0
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import re


@dataclass
class MacroParameter:
    """Macro parameter definition"""
    name: str
    type: str  # "string", "number", "identifier", "expression"
    default: Optional[Any] = None
    description: str = ""


@dataclass
class Macro:
    """Macro definition"""
    name: str
    parameters: List[MacroParameter]
    body: str  # Template body with $param placeholders
    description: str = ""
    
    def validate_args(self, args: Dict[str, Any]) -> bool:
        """Validate macro arguments against parameters"""
        # Check required parameters
        for param in self.parameters:
            if param.default is None and param.name not in args:
                raise ValueError(f"Missing required parameter: {param.name}")
        
        # Check parameter types
        for param_name, param_value in args.items():
            param_def = next((p for p in self.parameters if p.name == param_name), None)
            if param_def is None:
                raise ValueError(f"Unknown parameter: {param_name}")
            
            # Type checking
            if param_def.type == "number" and not isinstance(param_value, (int, float)):
                raise TypeError(f"Parameter {param_name} must be a number, got {type(param_value)}")
            elif param_def.type == "string" and not isinstance(param_value, str):
                raise TypeError(f"Parameter {param_name} must be a string, got {type(param_value)}")
        
        return True
    
    def expand(self, args: Dict[str, Any]) -> str:
        """Expand macro with given arguments"""
        self.validate_args(args)
        
        # Fill in defaults
        final_args = {}
        for param in self.parameters:
            if param.name in args:
                final_args[param.name] = args[param.name]
            elif param.default is not None:
                final_args[param.name] = param.default
        
        # Expand template
        result = self.body
        for param in self.parameters:
            param_name = param.name
            if param_name not in final_args:
                continue
            
            param_value = final_args[param_name]
            placeholder = f"${param_name}"
            
            # Format value based on parameter type
            if param.type == "string":
                # String values need quotes (but don't add if already quoted)
                if isinstance(param_value, str):
                    if not (param_value.startswith('"') and param_value.endswith('"')):
                        replacement = f'"{param_value}"'
                    else:
                        replacement = param_value
                else:
                    replacement = f'"{param_value}"'
            elif param.type == "identifier":
                # Identifiers should NOT have quotes
                replacement = str(param_value)
            elif param.type == "number":
                # Numbers as-is
                replacement = str(param_value)
            else:
                # Default: string representation
                replacement = str(param_value)
            
            result = result.replace(placeholder, replacement)
        
        return result


class MacroRegistry:
    """Global registry for macro definitions"""
    
    def __init__(self):
        self.macros: Dict[str, Macro] = {}
        self._load_builtin_macros()
    
    def register(self, macro: Macro):
        """Register a macro"""
        if macro.name in self.macros:
            raise ValueError(f"Macro '{macro.name}' already exists")
        self.macros[macro.name] = macro
    
    def get(self, name: str) -> Optional[Macro]:
        """Get a macro by name"""
        return self.macros.get(name)
    
    def expand(self, name: str, args: Dict[str, Any]) -> str:
        """Expand a macro"""
        macro = self.get(name)
        if macro is None:
            raise ValueError(f"Macro '{name}' not found")
        return macro.expand(args)
    
    def list_macros(self) -> List[str]:
        """List all available macros"""
        return list(self.macros.keys())
    
    def _load_builtin_macros(self):
        """Load built-in macros"""
        
        # Macro 1: Simple concept template
        self.register(Macro(
            name="simple_concept",
            parameters=[
                MacroParameter("name", "identifier", description="Concept name"),
                MacroParameter("definition", "string", description="Concept definition"),
                MacroParameter("baseline", "number", default=0.0, description="Baseline activation"),
            ],
            body="""concept $name {
    definition: $definition;
    baseline: $baseline;
    decay_rate: 0.1;
}""",
            description="Create a simple concept with baseline and decay"
        ))
        
        # Macro 2: Threshold inference
        self.register(Macro(
            name="threshold_inference",
            parameters=[
                MacroParameter("name", "identifier", description="Inference name"),
                MacroParameter("signal", "identifier", description="Signal to check"),
                MacroParameter("threshold", "number", description="Threshold value"),
                MacroParameter("concept", "identifier", description="Concept to increase"),
                MacroParameter("amount", "number", default=1.0, description="Increase amount"),
            ],
            body="""inference $name {
    when: (signals.$signal > $threshold);
    then: increase concept: "$concept" by $amount;
    mode: "symbolic";
}""",
            description="Create inference that triggers when signal exceeds threshold"
        ))
        
        # Macro 3: High priority intention
        self.register(Macro(
            name="high_priority_intention",
            parameters=[
                MacroParameter("name", "identifier", description="Intention name"),
                MacroParameter("goal", "string", description="Intention goal"),
                MacroParameter("action", "string", description="Action to perform"),
            ],
            body="""intention $name {
    priority: "high";
    goal: $goal;
    strategy: [
        if (true) then $action
    ];
}""",
            description="Create high-priority intention with single action"
        ))
        
        # Macro 4: Bidirectional association
        self.register(Macro(
            name="bidirectional_association",
            parameters=[
                MacroParameter("from_concept", "identifier", description="Source concept"),
                MacroParameter("to_concept", "identifier", description="Target concept"),
                MacroParameter("weight", "number", default=0.5, description="Association weight"),
            ],
            body="""associate $from_concept -> $to_concept {
    type: "reinforcement";
    weight: $weight;
    bidirectional: true;
}""",
            description="Create bidirectional association between concepts"
        ))
        
        # Macro 5: Empathy response pattern
        self.register(Macro(
            name="empathy_response",
            parameters=[
                MacroParameter("emotion", "identifier", description="Emotion to detect"),
                MacroParameter("threshold", "number", default=0.7, description="Emotion threshold"),
                MacroParameter("response", "string", description="Response message"),
            ],
            body="""inference detect_$emotion {
    when: (signals.$emotion > $threshold);
    then: say $response;
    mode: "symbolic";
    priority: "high";
}""",
            description="Create empathetic response to detected emotion"
        ))


class MacroExpander:
    """Expand macros in source code before parsing"""
    
    def __init__(self, registry: Optional[MacroRegistry] = None):
        self.registry = registry or MacroRegistry()
    
    def expand_source(self, source: str) -> str:
        """
        Expand all macros in source code.
        
        Macro syntax:
        @macro_name(param1: value1, param2: value2)
        
        Multi-line macro invocations are supported:
        @macro_name(
            param1: value1,
            param2: value2
        )
        
        Example:
        @simple_concept(name: user_intent, definition: "User's goal")
        """
        # Process source character by character to handle multi-line macros
        result = []
        i = 0
        
        while i < len(source):
            # Check for macro start
            if source[i] == '@' and (i == 0 or source[i-1] in '\n\t '):
                # Find macro name
                macro_start = i
                i += 1
                macro_name_chars = []
                
                while i < len(source) and (source[i].isalnum() or source[i] == '_'):
                    macro_name_chars.append(source[i])
                    i += 1
                
                if not macro_name_chars:
                    # Not a macro, just '@'
                    result.append('@')
                    continue
                
                macro_name = ''.join(macro_name_chars)
                
                # Skip whitespace
                while i < len(source) and source[i] in ' \t\n\r':
                    i += 1
                
                # Check for opening parenthesis
                if i >= len(source) or source[i] != '(':
                    # Not a macro invocation, keep as-is
                    result.append(source[macro_start:i])
                    continue
                
                # Find matching closing parenthesis
                i += 1  # Skip '('
                paren_count = 1
                args_chars = []
                
                while i < len(source) and paren_count > 0:
                    if source[i] == '(':
                        paren_count += 1
                    elif source[i] == ')':
                        paren_count -= 1
                    
                    if paren_count > 0:
                        args_chars.append(source[i])
                    
                    i += 1
                
                args_str = ''.join(args_chars)
                
                # Expand macro
                try:
                    args = self._parse_macro_args(args_str)
                    expanded = self.registry.expand(macro_name, args)
                    result.append(expanded)
                except Exception as e:
                    # If expansion fails, keep original with error comment
                    result.append(f"// ERROR: Failed to expand macro @{macro_name}: {e}\n")
                    result.append(source[macro_start:i])
            else:
                result.append(source[i])
                i += 1
        
        return ''.join(result)
    
    def _parse_macro_args(self, args_str: str) -> Dict[str, Any]:
        """
        Parse macro arguments.
        
        Format: name: value, name2: value2
        Values can be:
        - Numbers: 42, 3.14
        - Strings: "text", 'text'
        - Identifiers: concept_name
        """
        args = {}
        
        if not args_str.strip():
            return args
        
        # Split by commas (not inside quotes)
        parts = self._split_preserving_quotes(args_str, ',')
        
        for part in parts:
            part = part.strip()
            if ':' not in part:
                raise ValueError(f"Invalid macro argument format: {part} (expected 'name: value')")
            
            name, value = part.split(':', 1)
            name = name.strip()
            value = value.strip()
            
            # Parse value
            # String
            if (value.startswith('"') and value.endswith('"')) or \
               (value.startswith("'") and value.endswith("'")):
                args[name] = value[1:-1]  # Remove quotes
            # Number
            elif re.match(r'^-?\d+\.?\d*$', value):
                args[name] = float(value) if '.' in value else int(value)
            # Identifier (unquoted)
            else:
                args[name] = value
        
        return args
    
    def _split_preserving_quotes(self, text: str, delimiter: str) -> List[str]:
        """Split string by delimiter, preserving quoted sections"""
        parts = []
        current = []
        in_quotes = False
        quote_char = None
        
        for char in text:
            if char in ('"', "'") and (quote_char is None or char == quote_char):
                in_quotes = not in_quotes
                quote_char = char if in_quotes else None
                current.append(char)
            elif char == delimiter and not in_quotes:
                parts.append(''.join(current))
                current = []
            else:
                current.append(char)
        
        if current:
            parts.append(''.join(current))
        
        return parts


# Global macro registry
_global_registry = MacroRegistry()


def get_global_registry() -> MacroRegistry:
    """Get global macro registry"""
    return _global_registry


def expand_macros(source: str, registry: Optional[MacroRegistry] = None) -> str:
    """Expand macros in source code (convenience function)"""
    expander = MacroExpander(registry)
    return expander.expand_source(source)

