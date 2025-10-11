"""
ASPERA Language Parser
======================
Hand-rolled recursive descent parser for Aspera language.
Produces AST conforming to ast_schema.json.

Author: Christian Quintino De Luca - RTH Italia
Version: 0.3.0 (Enhanced Error Messages + Macro System)
"""

import re
import json
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import uuid
from difflib import get_close_matches
from aspera.lang.macros import expand_macros, MacroRegistry


class ErrorSuggestions:
    """Intelligent error suggestions and code examples"""
    
    # Keywords and common identifiers for "did you mean" suggestions
    KEYWORDS = [
        "concept", "associate", "state", "inference", "intention", "explain",
        "when", "then", "if", "else", "always", "and", "or", "not",
        "increase", "decrease", "set", "say", "trigger", "with", "by",
        "true", "false", "signals", "baseline", "decay_rate", "category",
        "definition", "from_concept", "to_concept", "type", "weight",
        "condition", "actions", "mode", "priority", "strategy"
    ]
    
    # Code examples for common errors
    EXAMPLES = {
        "concept": """
Example of correct concept syntax:
  concept user_intent {
    definition: "Represents user's primary goal";
    signals: ["keywords", "context"];
    baseline: 0.0;
    decay_rate: 0.1;
  }""",
        
        "associate": """
Example of correct associate syntax:
  associate user_intent -> engagement {
    type: "reinforcement";
    weight: 0.8;
  }""",
        
        "inference": """
Example of correct inference syntax:
  inference detect_urgency {
    when: (signals.urgency_score > 0.7);
    then: increase concept: "priority" by 0.5;
    mode: "symbolic";
  }""",
        
        "intention": """
Example of correct intention syntax:
  intention respond_to_user {
    trigger: "high_confidence";
    priority: "high";
    strategy: [
      if (concepts.empathy > 0.5) then "empathetic_response",
      else "standard_response"
    ];
  }""",
        
        "missing_semicolon": """
Example: Every statement must end with a semicolon
  ✗ Wrong:  baseline: 0.5
  ✓ Correct: baseline: 0.5;""",
        
        "missing_brace": """
Example: All blocks must have matching braces
  ✗ Wrong:  concept test {
              definition: "..."
  ✓ Correct: concept test {
              definition: "...";
            }""",
        
        "string_quotes": """
Example: Strings must be enclosed in double quotes
  ✗ Wrong:  definition: test
  ✓ Correct: definition: "test";""",
    }
    
    @staticmethod
    def suggest_keyword(typo: str) -> Optional[str]:
        """Suggest correction for misspelled keyword"""
        matches = get_close_matches(typo.lower(), ErrorSuggestions.KEYWORDS, n=1, cutoff=0.6)
        return matches[0] if matches else None
    
    @staticmethod
    def get_example(error_type: str) -> Optional[str]:
        """Get code example for error type"""
        return ErrorSuggestions.EXAMPLES.get(error_type)
    
    @staticmethod
    def build_hint(expected_type: str, context: Optional[str] = None) -> str:
        """Build contextual hint for error"""
        hints = {
            "SEMICOLON": "Every statement must end with a semicolon ';'. Did you forget one?",
            "RBRACE": "Missing closing brace '}'. Check that all blocks are properly closed.",
            "LBRACE": "Missing opening brace '{'. Block definitions must start with '{'.",
            "NUMBER": "Expected a number here (e.g., 0.5, 42, -3.14).",
            "STRING": "Expected a string in double quotes (e.g., \"text\").",
            "IDENTIFIER": "Expected an identifier (e.g., concept_name, variable_1).",
            "COLON": "Expected a colon ':' after the property name.",
            "LPAREN": "Expected an opening parenthesis '('.",
            "RPAREN": "Expected a closing parenthesis ')'. Check your conditions.",
            "CONCEPT": "Expected 'concept' keyword to define a new concept.",
            "INFERENCE": "Expected 'inference' keyword to define a rule.",
            "INTENTION": "Expected 'intention' keyword to define a behavior.",
        }
        
        hint = hints.get(expected_type, f"Expected {expected_type} here.")
        
        # Add context-specific hints
        if context:
            hint += f" Context: {context}"
        
        return hint


class Token:
    """Lexical token"""

    def __init__(self, type_: str, value: Any, line: int, col: int):
        self.type = type_
        self.value = value
        self.line = line
        self.col = col

    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, {self.line}:{self.col})"


class ParseError(Exception):
    """Parser error with location and rich context"""

    def __init__(
        self,
        message: str,
        line: int = 0,
        col: int = 0,
        source: Optional[str] = None,
        expected: Optional[List[str]] = None,
        got: Optional[str] = None,
        hint: Optional[str] = None,
        typo: Optional[str] = None,  # For "did you mean" suggestions
        error_category: str = "syntax",  # syntax, semantic, runtime
    ):
        self.line = line
        self.col = col
        self.source = source
        self.expected = expected
        self.got = got
        self.hint = hint
        self.typo = typo
        self.error_category = error_category
        
        # Build rich error message
        error_msg = self._build_error_message(message)
        super().__init__(error_msg)
    
    def _build_error_message(self, base_message: str) -> str:
        """Build a rich, developer-friendly error message"""
        lines = []
        
        # Error header with category
        category_emoji = {
            "syntax": "⚠️",
            "semantic": "❌",
            "runtime": "🔥"
        }
        emoji = category_emoji.get(self.error_category, "⚠️")
        
        if self.expected and self.got:
            expected_str = " or ".join(self.expected) if isinstance(self.expected, list) else self.expected
            lines.append(f"{emoji} Parse Error: Expected {expected_str}, got {self.got}")
        else:
            lines.append(f"{emoji} Parse Error: {base_message}")
        
        # Location
        lines.append(f"  at line {self.line}, column {self.col}")
        lines.append("")
        
        # Code context (if source available)
        if self.source and self.line > 0:
            source_lines = self.source.split("\n")
            context_start = max(0, self.line - 3)
            context_end = min(len(source_lines), self.line + 2)
            
            for i in range(context_start, context_end):
                line_num = i + 1
                line_content = source_lines[i] if i < len(source_lines) else ""
                
                # Current line marker
                marker = ">" if line_num == self.line else " "
                
                # Line number (right-aligned)
                lines.append(f"  {marker} {line_num:4d} | {line_content}")
                
                # Error indicator (^) under the problematic column
                if line_num == self.line and self.col > 0:
                    indent = " " * (len(f"  {marker} {line_num:4d} | ") + self.col - 1)
                    lines.append(f"{indent}^")
        
        lines.append("")
        
        # "Did you mean" suggestion
        if self.typo:
            suggestion = ErrorSuggestions.suggest_keyword(self.typo)
            if suggestion:
                lines.append(f"🤔 Did you mean '{suggestion}'?")
                lines.append("")
        
        # Hint (if provided)
        if self.hint:
            lines.append(f"💡 Hint: {self.hint}")
            lines.append("")
        
        # Code example (if available)
        if self.expected and len(self.expected) == 1:
            expected_lower = self.expected[0].lower()
            example = ErrorSuggestions.get_example(expected_lower)
            if example:
                lines.append(example)
                lines.append("")
        
        # Additional examples for common errors
        if self.expected:
            if "SEMICOLON" in self.expected:
                lines.append(ErrorSuggestions.EXAMPLES["missing_semicolon"])
                lines.append("")
            elif "RBRACE" in self.expected:
                lines.append(ErrorSuggestions.EXAMPLES["missing_brace"])
                lines.append("")
            elif "STRING" in self.expected and self.got == "IDENTIFIER":
                lines.append(ErrorSuggestions.EXAMPLES["string_quotes"])
                lines.append("")
        
        # Documentation link
        lines.append("📖 Documentation: https://github.com/rthgit/Aspera#language-reference")
        lines.append("❓ Need help? Open an issue: https://github.com/rthgit/Aspera/issues")
        
        return "\n".join(lines)


class Lexer:
    """Tokenizer for Aspera language"""

    TOKEN_PATTERNS = [
        ("COMMENT_LINE", r"//[^\n]*"),
        ("COMMENT_BLOCK", r"/\*.*?\*/"),
        ("CONCEPT", r"\bconcept\b"),
        ("ASSOCIATE", r"\bassociate\b"),
        ("STATE", r"\bstate\b"),
        ("INFERENCE", r"\binference\b"),
        ("INTENTION", r"\bintention\b"),
        ("EXPLAIN", r"\bexplain\b"),
        ("WHEN", r"\bwhen\b"),
        ("THEN", r"\bthen\b"),
        ("IF", r"\bif\b"),
        ("ELSE", r"\belse\b"),
        ("ALWAYS", r"\balways\b"),
        ("AND", r"\b(?i:and)\b"),
        ("OR", r"\b(?i:or)\b"),
        ("NOT", r"\b(?i:not)\b"),
        ("TRUE", r"\btrue\b"),
        ("FALSE", r"\bfalse\b"),
        ("INCREASE", r"\bincrease\b"),
        ("DECREASE", r"\bdecrease\b"),
        ("SET", r"\bset\b"),
        ("SAY", r"\bsay\b"),
        ("TRIGGER", r"\btrigger\b"),
        ("WITH", r"\bwith\b"),
        ("BY", r"\bby\b"),
        ("ARROW", r"->"),
        ("GTE", r">="),
        ("LTE", r"<="),
        ("EQ", r"=="),
        ("NEQ", r"!="),
        ("GT", r">"),
        ("LT", r"<"),
        ("LPAREN", r"\("),
        ("RPAREN", r"\)"),
        ("LBRACE", r"\{"),
        ("RBRACE", r"\}"),
        ("LBRACKET", r"\["),
        ("RBRACKET", r"\]"),
        ("COLON", r":"),
        ("SEMICOLON", r";"),
        ("COMMA", r","),
        ("DOT", r"\."),
        ("PLUS", r"\+"),
        ("MINUS", r"-"),
        ("STAR", r"\*"),
        ("SLASH", r"/"),
        ("PERCENT", r"%"),
        ("ASSIGN", r"="),
        ("STRING", r'"(?:[^"\\]|\\.)*"'),
        ("STRING_SINGLE", r"'(?:[^'\\]|\\.)*'"),
        ("NUMBER", r"-?\d+\.?\d*"),
        ("IDENTIFIER", r"[a-zA-Z_][a-zA-Z0-9_]*"),
        ("WHITESPACE", r"[ \t\n\r]+"),
    ]

    def __init__(self, source: str):
        self.source = source
        self.tokens: List[Token] = []
        self.pos = 0
        self.line = 1
        self.col = 1

    def tokenize(self) -> List[Token]:
        """Tokenize entire source"""
        compiled_patterns = [(name, re.compile(pattern)) for name, pattern in self.TOKEN_PATTERNS]

        while self.pos < len(self.source):
            matched = False
            for token_type, pattern in compiled_patterns:
                match = pattern.match(self.source, self.pos)
                if match:
                    raw_value = match.group(0)
                    value = raw_value
                    if token_type not in ("WHITESPACE", "COMMENT_LINE", "COMMENT_BLOCK"):
                        # Parse string literals
                        if token_type in ("STRING", "STRING_SINGLE"):
                            value = json.loads('"' + raw_value[1:-1] + '"')  # Unescape
                        # Parse numbers
                        elif token_type == "NUMBER":
                            value = float(raw_value) if "." in raw_value else int(raw_value)
                        # Parse booleans
                        elif token_type == "TRUE":
                            value = True
                        elif token_type == "FALSE":
                            value = False

                        self.tokens.append(Token(token_type, value, self.line, self.col))

                    # Update position (use raw_value for counting)
                    self.pos = match.end()
                    lines = raw_value.count("\n")
                    if lines > 0:
                        self.line += lines
                        self.col = len(raw_value.split("\n")[-1]) + 1
                    else:
                        self.col += len(raw_value)

                    matched = True
                    break

            if not matched:
                raise ParseError(f"Unexpected character: {self.source[self.pos]!r}", self.line, self.col)

        return self.tokens


class Parser:
    """Recursive descent parser for Aspera"""

    def __init__(self, tokens: List[Token], source: Optional[str] = None):
        self.tokens = tokens
        self.source = source  # Keep source for better error messages
        self.pos = 0

    def current(self) -> Optional[Token]:
        """Get current token"""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def peek(self, offset: int = 1) -> Optional[Token]:
        """Peek ahead"""
        if self.pos + offset < len(self.tokens):
            return self.tokens[self.pos + offset]
        return None

    def consume(self, expected_type: Optional[str] = None) -> Token:
        """Consume current token with enhanced error reporting"""
        token = self.current()
        if token is None:
            raise ParseError(
                "Unexpected end of file",
                line=self.tokens[-1].line if self.tokens else 0,
                col=self.tokens[-1].col if self.tokens else 0,
                source=self.source,
                hint="The file ended unexpectedly. Did you forget a closing brace '}' or semicolon ';'?",
                error_category="syntax"
            )
        if expected_type and token.type != expected_type:
            # Use ErrorSuggestions for better hints
            hint = ErrorSuggestions.build_hint(expected_type)
            
            # Detect "did you mean" for identifier misspellings
            typo = None
            if token.type == "IDENTIFIER" and expected_type in ["CONCEPT", "INFERENCE", "INTENTION", "ASSOCIATE"]:
                typo = str(token.value)
            
            raise ParseError(
                f"Expected {expected_type}, got {token.type}",
                line=token.line,
                col=token.col,
                source=self.source,
                expected=[expected_type],
                got=token.type,
                hint=hint,
                typo=typo,
                error_category="syntax"
            )
        self.pos += 1
        return token

    def match(self, *types: str) -> bool:
        """Check if current token matches any type"""
        token = self.current()
        return token is not None and token.type in types

    def parse(self) -> Dict[str, Any]:
        """Parse entire program"""
        nodes = []
        while self.current() is not None:
            node = self.parse_statement()
            if node:
                nodes.append(node)

        return {
            "version": "0.1.0",
            "nodes": nodes,
            "metadata": {
                "parsed_at": datetime.utcnow().isoformat() + "Z",
                "parser_version": "0.1.0"
            }
        }

    def parse_statement(self) -> Optional[Dict[str, Any]]:
        """Parse top-level statement"""
        if self.match("CONCEPT"):
            return self.parse_concept()
        elif self.match("ASSOCIATE"):
            return self.parse_associate()
        elif self.match("STATE"):
            return self.parse_state()
        elif self.match("INFERENCE"):
            return self.parse_inference()
        elif self.match("INTENTION"):
            return self.parse_intention()
        elif self.match("EXPLAIN"):
            return self.parse_explain()
        else:
            token = self.current()
            raise ParseError(f"Unexpected token: {token.type}", token.line, token.col)

    def parse_concept(self) -> Dict[str, Any]:
        """Parse concept block"""
        self.consume("CONCEPT")
        # Accept both STRING and IDENTIFIER for concept names
        if self.match("STRING"):
            name_token = self.consume("STRING")
        else:
            name_token = self.consume("IDENTIFIER")
        name = name_token.value

        self.consume("LBRACE")

        concept = {
            "type": "concept",
            "id": f"concept_{uuid.uuid4().hex[:8]}",
            "name": name
        }

        while not self.match("RBRACE"):
            key = self.consume("IDENTIFIER").value
            self.consume("COLON")

            if key == "definition":
                concept["definition"] = self.consume("STRING").value
            elif key == "signals":
                concept["signals"] = self.parse_string_list()
            elif key == "baseline":
                concept["baseline"] = self.parse_number()
            elif key == "decay_rate":
                concept["decay_rate"] = self.parse_number()
            elif key == "category":
                concept["category"] = self.consume("STRING").value
            else:
                # Suggest valid properties
                valid_props = ["definition", "signals", "baseline", "decay_rate", "category"]
                token = self.tokens[self.pos - 2] if self.pos >= 2 else None  # Get the property name token
                raise ParseError(
                    f"Unknown concept property: '{key}'",
                    line=token.line if token else 0,
                    col=token.col if token else 0,
                    source=self.source,
                    hint=f"Valid concept properties are: {', '.join(valid_props)}",
                    typo=key,
                    error_category="semantic"
                )

            self.consume("SEMICOLON")

        self.consume("RBRACE")
        return concept

    def parse_associate(self) -> Dict[str, Any]:
        """Parse associate block"""
        self.consume("ASSOCIATE")
        # Accept both STRING and IDENTIFIER for concept references
        if self.match("STRING"):
            from_concept = self.consume("STRING").value
        else:
            from_concept = self.consume("IDENTIFIER").value
        self.consume("ARROW")
        if self.match("STRING"):
            to_concept = self.consume("STRING").value
        else:
            to_concept = self.consume("IDENTIFIER").value
        self.consume("LBRACE")

        assoc = {
            "type": "associate",
            "id": f"assoc_{uuid.uuid4().hex[:8]}",
            "from_concept": from_concept,
            "to_concept": to_concept
        }

        while not self.match("RBRACE"):
            key = self.consume("IDENTIFIER").value
            self.consume("COLON")

            if key == "weight":
                assoc["weight"] = self.parse_number()
            elif key == "bidirectional":
                if self.match("TRUE"):
                    assoc["bidirectional"] = self.consume("TRUE").value
                else:
                    assoc["bidirectional"] = self.consume("FALSE").value
            elif key == "activation_threshold":
                assoc["activation_threshold"] = self.parse_number()
            elif key == "type" or key == "assoc_type":
                assoc["assoc_type"] = self.consume("STRING").value if self.match("STRING") else self.consume("IDENTIFIER").value
            else:
                # Suggest valid properties
                valid_props = ["weight", "bidirectional", "activation_threshold", "type"]
                token = self.tokens[self.pos - 2] if self.pos >= 2 else None
                raise ParseError(
                    f"Unknown associate property: '{key}'",
                    line=token.line if token else 0,
                    col=token.col if token else 0,
                    source=self.source,
                    hint=f"Valid associate properties are: {', '.join(valid_props)}",
                    typo=key,
                    error_category="semantic"
                )

            self.consume("SEMICOLON")

        self.consume("RBRACE")
        return assoc

    def parse_state(self) -> Dict[str, Any]:
        """Parse state block"""
        self.consume("STATE")
        self.consume("LBRACE")

        entries = {}
        while not self.match("RBRACE"):
            key = self.consume("IDENTIFIER").value
            self.consume("COLON")
            value = self.parse_value()
            self.consume("SEMICOLON")
            entries[key] = value

        self.consume("RBRACE")

        return {
            "type": "state",
            "id": f"state_{uuid.uuid4().hex[:8]}",
            "entries": entries
        }

    def parse_inference(self) -> Dict[str, Any]:
        """Parse inference block"""
        self.consume("INFERENCE")
        # Accept both STRING and IDENTIFIER for inference names
        if self.match("STRING"):
            name = self.consume("STRING").value
        else:
            name = self.consume("IDENTIFIER").value
        self.consume("LBRACE")

        inference = {
            "type": "inference",
            "id": f"inference_{uuid.uuid4().hex[:8]}",
            "name": name,
            "mode": "symbolic",  # default
            "priority": "medium"  # default
        }

        while not self.match("RBRACE"):
            # Accept both IDENTIFIER and keywords as property names
            has_colon = False
            if self.match("WHEN"):
                self.consume("WHEN")
                key = "when"
                # Optional colon (support both "when:" and "when (...)")
                if self.match("COLON"):
                    self.consume("COLON")
                    has_colon = True
            elif self.match("THEN"):
                self.consume("THEN")
                key = "then"
                # Optional colon (support both "then:" and "then ...")
                if self.match("COLON"):
                    self.consume("COLON")
                    has_colon = True
            else:
                key = self.consume("IDENTIFIER").value
                self.consume("COLON")
                has_colon = True

            if key == "when":
                inference["when_ast"] = self.parse_expression()
            elif key == "then":
                inference["then_action"] = self.parse_action()
                # Actions always end with semicolon
                if self.match("SEMICOLON"):
                    self.consume("SEMICOLON")
            elif key == "confidence":
                inference["confidence"] = self.parse_number()
            elif key == "priority":
                # Accept both "high" and "high" (identifier or string)
                if self.match("STRING"):
                    inference["priority"] = self.consume("STRING").value
                else:
                    inference["priority"] = self.consume("IDENTIFIER").value
            elif key == "mode":
                # Accept both "symbolic" and symbolic (identifier or string)
                if self.match("STRING"):
                    inference["mode"] = self.consume("STRING").value
                else:
                    inference["mode"] = self.consume("IDENTIFIER").value
            else:
                # Suggest valid properties
                valid_props = ["when", "then", "confidence", "priority", "mode"]
                token = self.tokens[self.pos - 2] if self.pos >= 2 else None
                raise ParseError(
                    f"Unknown inference property: '{key}'",
                    line=token.line if token else 0,
                    col=token.col if token else 0,
                    source=self.source,
                    hint=f"Valid inference properties are: {', '.join(valid_props)}",
                    typo=key,
                    error_category="semantic"
                )

            # Only consume semicolon if we had a colon (traditional syntax)
            # For 'then', semicolon is already consumed above
            if has_colon and key != "then":
                self.consume("SEMICOLON")

        self.consume("RBRACE")
        return inference

    def parse_intention(self) -> Dict[str, Any]:
        """Parse intention block"""
        self.consume("INTENTION")
        # Accept both STRING and IDENTIFIER for intention names
        if self.match("STRING"):
            name = self.consume("STRING").value
        else:
            name = self.consume("IDENTIFIER").value
        self.consume("LBRACE")

        intention = {
            "type": "intention",
            "id": f"intention_{uuid.uuid4().hex[:8]}",
            "name": name,
            "strategy": []
        }

        while not self.match("RBRACE"):
            key = self.consume("IDENTIFIER").value
            self.consume("COLON")

            if key == "priority":
                # Accept both "high" and high (identifier or string)
                if self.match("STRING"):
                    intention["priority"] = self.consume("STRING").value
                else:
                    intention["priority"] = self.consume("IDENTIFIER").value
            elif key == "goal":
                intention["goal"] = self.consume("STRING").value
            elif key == "timeout":
                intention["timeout"] = self.parse_number()
            elif key == "strategy":
                # Strategy can be either array syntax or list syntax
                if self.match("LBRACKET"):
                    intention["strategy"] = self.parse_strategy_array()
                else:
                    intention["strategy"] = self.parse_strategy_list()
            elif key == "trigger":
                # Accept both STRING and IDENTIFIER for trigger names
                if self.match("STRING"):
                    intention["trigger"] = self.consume("STRING").value
                else:
                    intention["trigger"] = self.consume("IDENTIFIER").value
            else:
                # Suggest valid properties
                valid_props = ["priority", "goal", "timeout", "strategy", "trigger"]
                token = self.tokens[self.pos - 2] if self.pos >= 2 else None
                raise ParseError(
                    f"Unknown intention property: '{key}'",
                    line=token.line if token else 0,
                    col=token.col if token else 0,
                    source=self.source,
                    hint=f"Valid intention properties are: {', '.join(valid_props)}",
                    typo=key,
                    error_category="semantic"
                )

            self.consume("SEMICOLON")

        self.consume("RBRACE")
        return intention

    def parse_explain(self) -> Dict[str, Any]:
        """Parse explain block"""
        self.consume("EXPLAIN")
        # Optional name (identifier or string) before the brace
        explain_name = None
        if self.match("STRING"):
            explain_name = self.consume("STRING").value
        elif self.match("IDENTIFIER"):
            explain_name = self.consume("IDENTIFIER").value
        self.consume("LBRACE")

        explain = {
            "type": "explain",
            "id": f"explain_{uuid.uuid4().hex[:8]}"
        }
        if explain_name:
            explain["name"] = explain_name

        while not self.match("RBRACE"):
            key = self.consume("IDENTIFIER").value
            self.consume("COLON")

            if key == "format":
                explain["format"] = self.consume("STRING").value
            elif key == "template":
                explain["template"] = self.consume("STRING").value
            elif key == "max_words":
                explain["max_words"] = self.parse_number()
            elif key == "tone":
                explain["tone"] = self.consume("STRING").value
            elif key == "context":
                explain["context"] = self.parse_string_list()
            else:
                # Suggest valid properties
                valid_props = ["format", "template", "max_words", "tone", "context"]
                token = self.tokens[self.pos - 2] if self.pos >= 2 else None
                raise ParseError(
                    f"Unknown explain property: '{key}'",
                    line=token.line if token else 0,
                    col=token.col if token else 0,
                    source=self.source,
                    hint=f"Valid explain properties are: {', '.join(valid_props)}",
                    typo=key,
                    error_category="semantic"
                )

            self.consume("SEMICOLON")

        self.consume("RBRACE")
        return explain

    def parse_expression(self) -> Dict[str, Any]:
        """Parse boolean/comparison expression"""
        return self.parse_or_expr()

    def parse_or_expr(self) -> Dict[str, Any]:
        """Parse OR expression"""
        left = self.parse_and_expr()

        while self.match("OR"):
            self.consume("OR")
            right = self.parse_and_expr()
            left = {
                "expr_type": "binary_op",
                "operator": "or",
                "left": left,
                "right": right
            }

        return left

    def parse_and_expr(self) -> Dict[str, Any]:
        """Parse AND expression"""
        left = self.parse_not_expr()

        while self.match("AND"):
            self.consume("AND")
            right = self.parse_not_expr()
            left = {
                "expr_type": "binary_op",
                "operator": "and",
                "left": left,
                "right": right
            }

        return left

    def parse_not_expr(self) -> Dict[str, Any]:
        """Parse NOT expression"""
        if self.match("NOT"):
            self.consume("NOT")
            operand = self.parse_comparison_expr()
            return {
                "expr_type": "unary_op",
                "operator": "not",
                "operand": operand
            }
        return self.parse_comparison_expr()

    def parse_comparison_expr(self) -> Dict[str, Any]:
        """Parse comparison expression"""
        left = self.parse_additive_expr()

        if self.match("GT", "LT", "GTE", "LTE", "EQ", "NEQ"):
            op_token = self.consume()
            op_map = {
                "GT": ">", "LT": "<", "GTE": ">=",
                "LTE": "<=", "EQ": "==", "NEQ": "!="
            }
            operator = op_map[op_token.type]
            right = self.parse_additive_expr()
            return {
                "expr_type": "binary_op",
                "operator": operator,
                "left": left,
                "right": right
            }

        return left

    def parse_additive_expr(self) -> Dict[str, Any]:
        """Parse addition/subtraction"""
        left = self.parse_mult_expr()

        while self.match("PLUS", "MINUS"):
            op = self.consume().type
            right = self.parse_mult_expr()
            left = {
                "expr_type": "binary_op",
                "operator": "+" if op == "PLUS" else "-",
                "left": left,
                "right": right
            }

        return left

    def parse_mult_expr(self) -> Dict[str, Any]:
        """Parse multiplication/division"""
        left = self.parse_primary_expr()

        while self.match("STAR", "SLASH", "PERCENT"):
            op_token = self.consume()
            op_map = {"STAR": "*", "SLASH": "/", "PERCENT": "%"}
            operator = op_map[op_token.type]
            right = self.parse_primary_expr()
            left = {
                "expr_type": "binary_op",
                "operator": operator,
                "left": left,
                "right": right
            }

        return left

    def parse_primary_expr(self) -> Dict[str, Any]:
        """Parse primary expression"""
        # Support unary minus for negative literals and expressions
        if self.match("MINUS"):
            self.consume("MINUS")
            operand = self.parse_primary_expr()
            if isinstance(operand, dict) and operand.get("expr_type") == "literal" and operand.get("value_type") == "number":
                return {"expr_type": "literal", "value": -operand["value"], "value_type": "number"}
            return {"expr_type": "unary_op", "operator": "neg", "operand": operand}
        if self.match("NUMBER"):
            value = self.consume("NUMBER").value
            return {"expr_type": "literal", "value": value, "value_type": "number"}

        if self.match("STRING"):
            value = self.consume("STRING").value
            return {"expr_type": "literal", "value": value, "value_type": "string"}

        if self.match("TRUE", "FALSE"):
            value = self.consume().value
            return {"expr_type": "literal", "value": value, "value_type": "boolean"}

        # Check for identifiers or keywords that can be used as identifiers in expressions
        # (like "concept", "state", etc.)
        if self.match("IDENTIFIER", "CONCEPT", "STATE"):
            # Get first part (could be IDENTIFIER or keyword)
            token = self.consume()
            if token.type == "IDENTIFIER":
                path = [token.value]
            else:
                # Convert keyword to lowercase string for identifier
                path = [token.type.lower()]

            # Dotted identifier
            while self.match("DOT"):
                self.consume("DOT")
                next_token = self.consume("IDENTIFIER")
                path.append(next_token.value)

            # Function call
            if self.match("LPAREN"):
                func_name = ".".join(path)
                self.consume("LPAREN")
                args = []
                while not self.match("RPAREN"):
                    args.append(self.parse_expression())
                    if self.match("COMMA"):
                        self.consume("COMMA")
                self.consume("RPAREN")
                return {
                    "expr_type": "function_call",
                    "function_name": func_name,
                    "arguments": args
                }

            return {"expr_type": "identifier", "path": path}

        if self.match("LPAREN"):
            self.consume("LPAREN")
            expr = self.parse_expression()
            self.consume("RPAREN")
            return expr

        token = self.current()
        raise ParseError(f"Unexpected token in expression: {token.type}", token.line, token.col)

    def parse_action(self) -> Dict[str, Any]:
        """Parse action"""
        if self.match("INCREASE"):
            return self.parse_increase_action()
        elif self.match("DECREASE"):
            return self.parse_decrease_action()
        elif self.match("SET"):
            return self.parse_set_action()
        elif self.match("SAY"):
            return self.parse_say_action()
        elif self.match("TRIGGER"):
            return self.parse_trigger_action()
        elif self.match("LBRACKET"):
            return self.parse_multi_action()
        else:
            token = self.current()
            raise ParseError(f"Expected action, got {token.type}", token.line, token.col)

    def parse_increase_action(self) -> Dict[str, Any]:
        """Parse increase action"""
        self.consume("INCREASE")
        self.consume("CONCEPT")  # concept keyword
        # Support both "concept: "name"" and "concept name"
        if self.match("COLON"):
            self.consume("COLON")
            concept = self.consume("STRING").value
        else:
            concept = self.consume("IDENTIFIER").value
        self.consume("BY")
        delta = self.parse_number()
        return {
            "action_type": "increase",
            "concept": concept,
            "delta": delta
        }

    def parse_decrease_action(self) -> Dict[str, Any]:
        """Parse decrease action"""
        self.consume("DECREASE")
        self.consume("CONCEPT")  # concept keyword
        # Support both "concept: "name"" and "concept name"
        if self.match("COLON"):
            self.consume("COLON")
            concept = self.consume("STRING").value
        else:
            concept = self.consume("IDENTIFIER").value
        self.consume("BY")
        delta = self.parse_number()
        return {
            "action_type": "decrease",
            "concept": concept,
            "delta": delta
        }

    def parse_set_action(self) -> Dict[str, Any]:
        """Parse set action"""
        self.consume("SET")
        path = [self.consume("IDENTIFIER").value]
        while self.match("DOT"):
            self.consume("DOT")
            path.append(self.consume("IDENTIFIER").value)
        self.consume("ASSIGN")
        value = self.parse_value()
        return {
            "action_type": "set",
            "target": path,
            "value": value
        }

    def parse_say_action(self) -> Dict[str, Any]:
        """Parse say action"""
        self.consume("SAY")
        # Accept both "message" and message (identifier or string)
        if self.match("STRING"):
            message = self.consume("STRING").value
        else:
            message = self.consume("IDENTIFIER").value
        return {
            "action_type": "say",
            "message": message
        }

    def parse_trigger_action(self) -> Dict[str, Any]:
        """Parse trigger action"""
        self.consume("TRIGGER")
        # Accept both "event_name" and event_name (identifier or string)
        if self.match("STRING"):
            event_name = self.consume("STRING").value
        else:
            event_name = self.consume("IDENTIFIER").value
        action = {
            "action_type": "trigger",
            "event_name": event_name
        }
        if self.match("WITH"):
            self.consume("WITH")
            action["data"] = self.parse_value()
        return action

    def parse_multi_action(self) -> Dict[str, Any]:
        """Parse multiple actions"""
        self.consume("LBRACKET")
        actions = []
        while not self.match("RBRACKET"):
            actions.append(self.parse_action())
            if self.match("COMMA"):
                self.consume("COMMA")
        self.consume("RBRACKET")
        return {
            "action_type": "multi",
            "actions": actions
        }

    def parse_strategy_array(self) -> List[Dict[str, Any]]:
        """Parse strategy array syntax: [if (cond) then "action", ...]"""
        self.consume("LBRACKET")
        strategies = []
        
        while not self.match("RBRACKET"):
            if self.match("IF"):
                self.consume("IF")
                condition = self.parse_expression()
                self.consume("THEN")
                action = self.consume("STRING").value
                strategies.append({
                    "rule_type": "if",
                    "condition": condition,
                    "action": action
                })
            elif self.match("ELSE"):
                self.consume("ELSE")
                action = self.consume("STRING").value
                strategies.append({
                    "rule_type": "else",
                    "action": action
                })
            elif self.match("ALWAYS"):
                self.consume("ALWAYS")
                action = self.consume("STRING").value
                strategies.append({
                    "rule_type": "always",
                    "action": action
                })
            
            # Consume comma if present
            if self.match("COMMA"):
                self.consume("COMMA")
        
        self.consume("RBRACKET")
        return strategies
    
    def parse_strategy_list(self) -> List[Dict[str, Any]]:
        """Parse strategy list"""
        strategies = []
        while self.match("MINUS"):
            self.consume("MINUS")
            if self.match("IF"):
                self.consume("IF")
                condition = self.parse_expression()
                self.consume("ARROW")
                self.consume("IDENTIFIER")  # action keyword
                self.consume("COLON")
                action = self.consume("STRING").value
                strategies.append({
                    "rule_type": "if",
                    "condition": condition,
                    "action": action
                })
            elif self.match("ELSE"):
                self.consume("ELSE")
                self.consume("ARROW")
                self.consume("IDENTIFIER")  # action keyword
                self.consume("COLON")
                action = self.consume("STRING").value
                strategies.append({
                    "rule_type": "else",
                    "action": action
                })
            elif self.match("ALWAYS"):
                self.consume("ALWAYS")
                self.consume("ARROW")
                self.consume("IDENTIFIER")  # action keyword
                self.consume("COLON")
                action = self.consume("STRING").value
                strategies.append({
                    "rule_type": "always",
                    "action": action
                })
        return strategies

    def parse_string_list(self) -> List[str]:
        """Parse list of strings"""
        self.consume("LBRACKET")
        items = []
        while not self.match("RBRACKET"):
            items.append(self.consume("STRING").value)
            if self.match("COMMA"):
                self.consume("COMMA")
        self.consume("RBRACKET")
        return items

    def parse_number(self) -> float:
        """Parse number value, handling negative numbers"""
        negative = False
        if self.match("MINUS"):
            self.consume("MINUS")
            negative = True
        value = self.consume("NUMBER").value
        return -value if negative else value
    
    def parse_value(self) -> Any:
        """Parse generic value (number, string, bool, list, object)"""
        # Handle numbers (including negative)
        if self.match("MINUS") or self.match("NUMBER"):
            return self.parse_number()
        elif self.match("STRING"):
            return self.consume("STRING").value
        elif self.match("TRUE", "FALSE"):
            return self.consume().value
        elif self.match("LBRACKET"):
            return self.parse_list()
        elif self.match("LBRACE"):
            return self.parse_object()
        else:
            token = self.current()
            raise ParseError(f"Expected value, got {token.type}", token.line, token.col)

    def parse_list(self) -> List[Any]:
        """Parse list"""
        self.consume("LBRACKET")
        items = []
        while not self.match("RBRACKET"):
            items.append(self.parse_value())
            if self.match("COMMA"):
                self.consume("COMMA")
        self.consume("RBRACKET")
        return items

    def parse_object(self) -> Dict[str, Any]:
        """Parse object"""
        self.consume("LBRACE")
        obj = {}
        while not self.match("RBRACE"):
            key = self.consume("IDENTIFIER").value
            self.consume("COLON")
            obj[key] = self.parse_value()
            if self.match("COMMA"):
                self.consume("COMMA")
        self.consume("RBRACE")
        return obj


def parse_aspera(source: str) -> Dict[str, Any]:
    """
    Parse Aspera source code into AST.
    
    Args:
        source: Aspera source code
        
    Returns:
        AST dictionary conforming to ast_schema.json
        
    Raises:
        ParseError: On syntax error
    """
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens, source=source)
    ast = parser.parse()
    return ast


def validate_ast(ast: Dict[str, Any], schema_path: str = None) -> bool:
    """
    Validate AST against JSON schema.
    
    Args:
        ast: AST dictionary
        schema_path: Path to ast_schema.json (optional)
        
    Returns:
        True if valid
        
    Raises:
        jsonschema.ValidationError: If invalid
    """
    import jsonschema
    import os

    if schema_path is None:
        schema_path = os.path.join(os.path.dirname(__file__), "ast_schema.json")

    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    jsonschema.validate(ast, schema)
    return True


def parse_aspera_with_macros(source: str, macro_registry: Optional[MacroRegistry] = None) -> Dict[str, Any]:
    """
    Parse Aspera source code with macro expansion.
    
    Args:
        source: Aspera source code (may contain macro invocations)
        macro_registry: Custom macro registry (optional, uses global if not provided)
        
    Returns:
        AST dictionary
        
    Example:
        source = '''
        @simple_concept(name: user_intent, definition: "User's goal", baseline: 0.5)
        
        @threshold_inference(
            name: detect_urgency,
            signal: urgency_score,
            threshold: 0.7,
            concept: priority,
            amount: 0.5
        )
        '''
        
        ast = parse_aspera_with_macros(source)
    """
    # Expand macros first
    expanded_source = expand_macros(source, macro_registry)
    
    # Parse expanded source
    return parse_aspera(expanded_source)


def parse_file_with_macros(file_path: str, macro_registry: Optional[MacroRegistry] = None) -> Dict[str, Any]:
    """
    Parse Aspera file with macro expansion.
    
    Args:
        file_path: Path to .aspera file
        macro_registry: Custom macro registry (optional)
        
    Returns:
        AST dictionary
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        source = f.read()
    
    return parse_aspera_with_macros(source, macro_registry)


if __name__ == "__main__":
    # Test parser with simple example
    test_source = '''
    concept "test" {
        definition: "a test concept";
        baseline: 0.5;
    }
    '''

    try:
        ast = parse_aspera(test_source)
        print(json.dumps(ast, indent=2))
    except ParseError as e:
        print(f"Parse error: {e}")

