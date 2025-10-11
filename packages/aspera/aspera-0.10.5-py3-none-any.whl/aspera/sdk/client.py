"""
ASPERA SDK Client
==================
High-level API per utilizzare ASPERA facilmente.

Author: Christian Quintino De Luca - RTH Italia
"""

from typing import Any, Dict, Optional, Union
import json
import logging
from dotenv import load_dotenv

# Carica variabili d'ambiente dal file .env
load_dotenv()

from aspera.lang.parser import parse_aspera, validate_ast
from aspera.lang.module_loader import load_module_with_imports
from aspera.runtime.engine import CognitiveEngine

logger = logging.getLogger(__name__)


def create_engine(
    source: Union[str, Dict[str, Any]],
    use_mock_llm: bool = False,
    groq_api_key: Optional[str] = None,
    auto_detect: bool = True,
    enable_cache: bool = True
) -> CognitiveEngine:
    """
    Crea un CognitiveEngine da file .aspera o AST.

    Args:
        source: Path al file .aspera, stringa di codice Aspera, o AST dictionary
        use_mock_llm: Se True, forza uso di mock LLM (default: False, usa Groq se GROQ_API_KEY presente)
        groq_api_key: Groq API key (opzionale, legge da env se None)
        auto_detect: Se True, usa automaticamente Groq se chiave disponibile, altrimenti mock (default: True)
        enable_cache: Se True, abilita caching intelligente (default: True, ~50% riduzione costi)

    Returns:
        CognitiveEngine pronto all'uso

    Raises:
        ParseError: Se il parsing fallisce
        FileNotFoundError: Se il file non esiste

    Example:
        >>> engine = create_engine("examples/empathetic.aspera")  # Auto-detect: usa Groq se GROQ_API_KEY è set
        >>> engine = create_engine(ast_dict, groq_api_key="gsk_...")  # Forza Groq con chiave specifica
        >>> engine = create_engine("test.aspera", use_mock_llm=True)  # Forza mock per testing
        >>> engine = create_engine("test.aspera", enable_cache=False)  # Disabilita cache
    """
    # Determina tipo di input
    if isinstance(source, dict):
        # È già un AST
        ast = source
        logger.info("Using provided AST dictionary")
    elif isinstance(source, str):
        # Potrebbe essere file path o codice
        if source.endswith(".aspera") or "/" in source or "\\" in source:
            # Probabilmente un file path - usa module loader per supportare import
            try:
                import os
                base_dir = os.path.dirname(os.path.abspath(source))
                ast = load_module_with_imports(source, base_dir)
                logger.info(f"Loaded Aspera module with imports from file: {source}")
            except FileNotFoundError:
                logger.error(f"File not found: {source}")
                raise
        else:
            # È codice inline - parse diretto
            code = source
            logger.info("Using inline Aspera code")
            ast = parse_aspera(code)
            logger.info("Aspera code parsed successfully")

        # Valida (opzionale ma raccomandato)
        try:
            validate_ast(ast)
            logger.info("AST validation successful")
        except Exception as e:
            logger.warning(f"AST validation failed: {e}")
    else:
        raise ValueError("source must be file path, Aspera code string, or AST dict")

    # Determina se usare mock o Groq
    import os
    if auto_detect and not use_mock_llm:
        # Auto-detect: usa Groq se chiave disponibile
        has_key = groq_api_key or os.getenv("GROQ_API_KEY")
        if not has_key:
            logger.warning("GROQ_API_KEY non trovata - usando Mock LLM. Per usare Groq reale, imposta GROQ_API_KEY in .env")
            use_mock_llm = True
        else:
            logger.info("GROQ_API_KEY trovata - usando Groq LLM reale")
            use_mock_llm = False
    
    # Crea engine
    engine = CognitiveEngine(
        use_mock_llm=use_mock_llm, 
        groq_api_key=groq_api_key,
        enable_cache=enable_cache
    )
    engine.load_ast(ast)

    cache_status = "enabled" if enable_cache else "disabled"
    logger.info(f"CognitiveEngine created (LLM: {'Mock' if use_mock_llm else 'Groq'}, Cache: {cache_status}) - AST loaded")
    return engine


def run_observation(
    engine: CognitiveEngine,
    signals: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None,
    explain: bool = True
) -> Dict[str, Any]:
    """
    Esegue un'osservazione completa: observe → step → decide → explain.

    Args:
        engine: CognitiveEngine instance
        signals: Segnali di input
        context: Contesto aggiuntivo (experiences, etc.)
        explain: Se True, genera spiegazione

    Returns:
        Dictionary con:
            - step_result: Risultato del reasoning step
            - actions: Azioni selezionate
            - explanation: Spiegazione (se explain=True)
            - audit_trace: Audit trail completo

    Example:
        >>> result = run_observation(
        ...     engine,
        ...     signals={"coerenza_comportamento": 0.7, "trasparenza": 0.8},
        ...     context={"experiences": {"shared": 5}}
        ... )
        >>> print(result["actions"])
        >>> print(result["explanation"])
    """
    logger.info("Running observation cycle...")

    # 1. Observe
    engine.observe(signals, context)

    # 2. Step (reasoning)
    step_result = engine.step()

    # 3. Decide (policy execution)
    actions = engine.decide()

    # 4. Explain (optional)
    explanation = None
    if explain:
        explanation = engine.explain()

    # 5. Get audit trail
    audit_trace = engine.get_audit_trail()

    result = {
        "step_result": step_result,
        "actions": actions,
        "explanation": explanation,
        "audit_trace": audit_trace,
        "state_snapshot": engine.get_state_snapshot()
    }

    logger.info("Observation cycle completed")
    return result


def serialize_state(engine: CognitiveEngine) -> Dict[str, Any]:
    """
    Serializza lo stato del cognitive engine in formato JSON-friendly.

    Args:
        engine: CognitiveEngine instance

    Returns:
        Dictionary serializzabile con stato completo

    Example:
        >>> state = serialize_state(engine)
        >>> with open("state.json", "w") as f:
        ...     json.dump(state, f, indent=2)
    """
    return engine.get_state_snapshot()


def load_examples(example_name: Optional[str] = None) -> Union[str, Dict[str, str]]:
    """
    Carica esempi .aspera inclusi.

    Args:
        example_name: Nome esempio (empathetic, collaborative, analytical) o None per tutti

    Returns:
        Path al file esempio o dict con tutti gli esempi

    Example:
        >>> empathetic_path = load_examples("empathetic")
        >>> all_examples = load_examples()
    """
    import os

    examples_dir = os.path.join(os.path.dirname(__file__), "..", "lang", "examples")
    examples = {
        "empathetic": os.path.join(examples_dir, "empathetic.aspera"),
        "collaborative": os.path.join(examples_dir, "collaborative.aspera"),
        "analytical": os.path.join(examples_dir, "analytical.aspera"),
    }

    if example_name:
        if example_name in examples:
            return examples[example_name]
        else:
            raise ValueError(f"Unknown example: {example_name}. Available: {list(examples.keys())}")
    else:
        return examples

