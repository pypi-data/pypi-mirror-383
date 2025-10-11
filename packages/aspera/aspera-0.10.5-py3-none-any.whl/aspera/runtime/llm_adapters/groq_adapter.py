"""
ASPERA Groq LLM Adapter
========================
Integrazione con Groq API per reasoning complesso e spiegazioni naturali.
Usa GROQ_API_KEY da variabili d'ambiente.

Author: Christian Quintino De Luca - RTH Italia
"""

import os
import json
import logging
from typing import Any, Dict, List, Optional
from groq import Groq
from groq import APIError, RateLimitError

logger = logging.getLogger(__name__)


class GroqAdapter:
    """
    Adapter per Groq LLM.
    
    Gestisce:
    - Inferenze complesse che richiedono reasoning LLM
    - Generazione di spiegazioni naturali
    - Analisi di policy strategiche
    """

    # Prompt templates
    INFERENCE_PROMPT = """You are a cognition engine. Given CONTEXT, SIGNALS, and RULES, apply rules and output valid JSON:
{{"changes":[{{"concept":str,"delta":float}}], "confidence":float, "rationale":str}}

CONTEXT: {context_json}
SIGNALS: {signals_json}
RULES: {rules_text}

Respond with ONLY valid JSON, no other text."""

    EXPLAIN_PROMPT = """You are a transparent assistant. Given OBSERVATION and INFERENCES, produce a human explanation following TEMPLATE:

TEMPLATE: "{template}"
OBSERVATION: {observation}
INFERENCES: {inferences}

Keep <= {max_words} words, {tone} tone. Output only the explanation text, no preamble."""

    POLICY_PROMPT = """Translate STRATEGY rules and STATE into ordered actions JSON:
{{"actions":[{{"action":str,"reason":str,"priority":"high|medium|low"}}]}}

STATE: {state_json}
STRATEGY: {strategy_json}

Respond with ONLY valid JSON, no other text."""

    def __init__(self, api_key: Optional[str] = None,
                 model: str = "llama-3.3-70b-versatile",
                 max_tokens: int = 512,
                 temperature: float = 0.7):
        """
        Inizializza Groq adapter.

        Args:
            api_key: Groq API key (se None, legge da env GROQ_API_KEY)
            model: Modello da usare
            max_tokens: Token massimi per risposta
            temperature: Temperature per sampling (0-1)

        Raises:
            ValueError: Se API key non è fornita o trovata
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GROQ_API_KEY not found. "
                "Set it via environment variable or pass to constructor. "
                "Get your key at: https://console.groq.com"
            )

        self.model = model or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.max_tokens = int(os.getenv("GROQ_MAX_TOKENS", max_tokens))
        self.temperature = float(os.getenv("GROQ_TEMPERATURE", temperature))

        # Inizializza client Groq
        try:
            self.client = Groq(api_key=self.api_key)
            logger.info(f"GroqAdapter initialized (model={self.model})")
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")
            raise

        # Statistiche
        self.stats = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "total_tokens": 0
        }

    def infer(self, prompt: str, context: Optional[Dict[str, Any]] = None,
              max_tokens: Optional[int] = None,
              temperature: Optional[float] = None) -> str:
        """
        ASPERA-compatible inference method.
        
        Args:
            prompt: Prompt completo
            context: Context dict (opzionale, per compatibilità ASPERA)
            max_tokens: Override max_tokens
            temperature: Override temperature

        Returns:
            Risposta come stringa

        Raises:
            Exception: Su errore API o parsing
        """
        self.stats["total_calls"] += 1

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a precise reasoning engine. Always respond with valid JSON when requested."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=int(max_tokens or self.max_tokens),
                temperature=float(temperature or self.temperature),
            )

            content = response.choices[0].message.content.strip()
            
            # Update stats
            if hasattr(response, 'usage'):
                self.stats["total_tokens"] += response.usage.total_tokens

            self.stats["successful_calls"] += 1
            return content

        except RateLimitError as e:
            self.stats["failed_calls"] += 1
            logger.error(f"Groq rate limit exceeded: {e}")
            raise
    
    def infer_json(self, prompt: str, max_tokens: Optional[int] = None,
                   temperature: Optional[float] = None) -> Dict[str, Any]:
        """
        Esegue inferenza LLM e ritorna JSON parsato.

        Args:
            prompt: Prompt completo
            max_tokens: Override max_tokens
            temperature: Override temperature

        Returns:
            Dizionario parsato dalla risposta JSON

        Raises:
            Exception: Su errore API o parsing
        """
        content = self.infer(prompt, None, max_tokens, temperature)
        
        # Prova a parsare come JSON
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse LLM response as JSON: {content[:100]}")
            # Ritorna come testo
            return {"text": content}

    def generate_inference(self, context: Dict[str, Any],
                          signals: Dict[str, Any],
                          rules: List[str]) -> Dict[str, Any]:
        """
        Genera inferenza usando LLM.

        Args:
            context: Contesto corrente
            signals: Segnali di input
            rules: Lista di regole testuali

        Returns:
            {changes: [...], confidence: float, rationale: str}
        """
        prompt = self.INFERENCE_PROMPT.format(
            context_json=json.dumps(context, indent=2),
            signals_json=json.dumps(signals, indent=2),
            rules_text="\n".join(f"- {r}" for r in rules)
        )

        logger.debug(f"Generating LLM inference...")
        result = self.infer_json(prompt)
        # Auto-repair minimo: garantisce chiavi base
        if not isinstance(result, dict):
            try:
                result = json.loads(str(result))
            except Exception:
                result = {}
        
        # Valida struttura
        if "changes" not in result:
            result["changes"] = []
        if "confidence" not in result:
            result["confidence"] = 0.5
        if "rationale" not in result:
            result["rationale"] = "Generated by LLM"

        return result

    def generate_explanation(self, template: str, observation: Dict[str, Any],
                            inferences: List[Dict[str, Any]],
                            max_words: int = 40, tone: str = "warm") -> str:
        """
        Genera spiegazione naturale seguendo template.

        Args:
            template: Template con placeholder [interpretation], [evidence], etc.
            observation: Osservazione corrente
            inferences: Lista di inferenze applicate
            max_words: Lunghezza massima
            tone: Tono della spiegazione

        Returns:
            Stringa di spiegazione
        """
        prompt = self.EXPLAIN_PROMPT.format(
            template=template,
            observation=json.dumps(observation, indent=2),
            inferences=json.dumps(inferences, indent=2),
            max_words=max_words,
            tone=tone
        )

        logger.debug(f"Generating LLM explanation...")
        # A/B leggero su temperatura: preferisci il testo più conciso
        best_text = None
        best_len = 10**9
        for temp in (0.7, 0.9):
            res = self.infer(prompt, None, None, temp)
            text = res if isinstance(res, str) else str(res)
            if text and len(text) < best_len:
                best_text, best_len = text, len(text)
        return best_text or ""

    def generate_policy_actions(self, state: Dict[str, Any],
                                strategy: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Traduce strategie in azioni prioritizzate usando LLM.

        Args:
            state: Stato corrente
            strategy: Lista di regole strategiche

        Returns:
            Lista di {action: str, reason: str, priority: str}
        """
        prompt = self.POLICY_PROMPT.format(
            state_json=json.dumps(state, indent=2),
            strategy_json=json.dumps(strategy, indent=2)
        )

        logger.debug(f"Generating LLM policy actions...")
        # A/B test su temperatura: scegli il set con più azioni
        best_actions: List[Dict[str, Any]] = []
        for temp in (0.6, 0.9):
            try:
                raw = self.infer(prompt, None, None, temp)
                parsed = json.loads(raw) if isinstance(raw, str) else raw
            except Exception:
                parsed = {}
            actions = parsed.get("actions") if isinstance(parsed, dict) else None
            if isinstance(actions, list) and len(actions) > len(best_actions):
                best_actions = actions
        if best_actions:
            return best_actions
        # Fallback a infer_json standard
        result = self.infer_json(prompt)
        return result.get("actions", [])

    def get_stats(self) -> Dict[str, Any]:
        """Ritorna statistiche di utilizzo"""
        return self.stats.copy()

    def __repr__(self):
        return f"GroqAdapter(model={self.model}, calls={self.stats['total_calls']})"


class MockGroqAdapter:
    """
    Mock adapter per testing senza API key.
    Ritorna risposte predefinite invece di chiamare Groq.
    """

    def __init__(self, **kwargs):
        logger.info("MockGroqAdapter initialized (no real API calls)")
        self.stats = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "total_tokens": 0
        }

    def infer(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Mock infer - ritorna risposta fissa"""
        self.stats["total_calls"] += 1
        self.stats["successful_calls"] += 1
        self.stats["total_tokens"] += 100

        return {
            "text": "[MOCK RESPONSE] This is a simulated LLM response for testing.",
            "confidence": 0.7
        }

    def generate_inference(self, context, signals, rules) -> Dict[str, Any]:
        """Mock inference"""
        self.stats["total_calls"] += 1
        self.stats["successful_calls"] += 1
        return {
            "changes": [{"concept": "mock_concept", "delta": 0.1}],
            "confidence": 0.7,
            "rationale": "[MOCK] Inference generated in mock mode."
        }

    def generate_explanation(self, template, observation, inferences, **kwargs) -> str:
        """Mock explanation"""
        self.stats["total_calls"] += 1
        self.stats["successful_calls"] += 1
        return "[MOCK EXPLANATION] This is a simulated explanation for testing purposes."

    def generate_policy_actions(self, state, strategy) -> List[Dict[str, Any]]:
        """Mock policy actions"""
        self.stats["total_calls"] += 1
        self.stats["successful_calls"] += 1
        return [
            {"action": "mock_action", "reason": "Mock reasoning", "priority": "medium"}
        ]

    def get_stats(self) -> Dict[str, Any]:
        return self.stats.copy()

    def __repr__(self):
        return "MockGroqAdapter(mock mode, no real API calls)"

