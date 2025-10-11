"""
ASPERA Cognitive Engine
========================
Motore cognitivo centrale che orchestra:
- Symbolic Reasoner (inferenze deterministiche)
- LLM Adapter (reasoning complesso e spiegazioni)
- Memory System (episodica e semantica)
- Policy Executor (strategie di alto livello)

Author: Christian Quintino De Luca - RTH Italia
"""

from typing import Any, Dict, List, Optional
import logging
from copy import deepcopy
import time

from aspera.runtime.symbolic import SymbolicReasoner
from aspera.runtime.memory import MemorySystem
from aspera.runtime.policy import PolicyExecutor
from aspera.runtime.thresholds import get_thresholds
from aspera.runtime.llm_adapters.groq_adapter import GroqAdapter, MockGroqAdapter
from aspera.runtime.cache import AsperaCache, get_cache
from aspera.runtime.resource_limits import ResourceMonitor, ResourceLimits, ResourceTier, ResourceLimitExceeded
from aspera.runtime.error_handler import (
    CircuitBreaker,
    retry_with_backoff,
    log_error_structured,
)
from aspera.runtime.otel import init_otel
from opentelemetry import trace, metrics

logger = logging.getLogger(__name__)


class CognitiveEngine:
    """
    Motore cognitivo centrale di ASPERA.
    
    Carica un AST Aspera e lo esegue orchestrando:
    - Ragionamento simbolico (regole deterministiche)
    - Ragionamento LLM (inferenze complesse)
    - Memoria (episodica/semantica)
    - Policy execution (strategie)
    """

    def __init__(
        self, 
        use_mock_llm: bool = False, 
        groq_api_key: Optional[str] = None,
        enable_cache: bool = True,
        cache_instance: Optional[AsperaCache] = None,
        resource_tier: ResourceTier = ResourceTier.PRO,
        custom_limits: Optional[ResourceLimits] = None
    ):
        """
        Inizializza il cognitive engine.

        Args:
            use_mock_llm: Se True, usa MockGroqAdapter invece di vero LLM
            groq_api_key: Groq API key (opzionale, legge da env se None)
            enable_cache: Se True, abilita il caching intelligente (default: True)
            resource_tier: Tier per resource limits (default: PRO)
            custom_limits: Custom resource limits (override tier)
            cache_instance: Istanza cache personalizzata (opzionale)
        """
        # Componenti
        self.symbolic_reasoner = SymbolicReasoner()
        self.memory = MemorySystem()
        self.policy_executor = PolicyExecutor(self.symbolic_reasoner)

        # Caching
        self.enable_cache = enable_cache
        if enable_cache:
            self.cache = cache_instance if cache_instance is not None else get_cache()
            logger.info("Caching enabled (50%+ cost reduction expected)")
        else:
            self.cache = None
            logger.info("Caching disabled")

        # LLM Adapter
        if use_mock_llm:
            self.llm = MockGroqAdapter()
            logger.info("Using MockGroqAdapter (no real API calls)")
        else:
            try:
                self.llm = GroqAdapter(api_key=groq_api_key)
                logger.info("Using real GroqAdapter")
            except ValueError as e:
                logger.warning(f"Failed to initialize GroqAdapter: {e}. Falling back to mock.")
                self.llm = MockGroqAdapter()

        # Resource Limits
        limits = custom_limits if custom_limits else ResourceLimits.for_tier(resource_tier)
        self.resource_monitor = ResourceMonitor(limits)
        logger.info(f"Resource limits: {resource_tier.value} tier")
        
        # AST caricato
        self.ast: Optional[Dict[str, Any]] = None
        self.concepts: Dict[str, float] = {}
        self.associations: List[Dict[str, Any]] = []
        self.state: Dict[str, Any] = {}
        self.inferences: List[Dict[str, Any]] = []
        self.intentions: List[Dict[str, Any]] = []
        self.explain_config: Optional[Dict[str, Any]] = None

        # Audit trail
        self.execution_log: List[Dict[str, Any]] = []

        # LLM resilience
        self._llm_cb = CircuitBreaker(failure_threshold=3, timeout=30, name="llm")

        # Metrics
        self.metrics: Dict[str, Any] = {
            "durations": {},
            "counts": {"applied_inferences": 0, "actions": 0}
        }

        logger.info("CognitiveEngine initialized")
        # OpenTelemetry (best effort)
        try:
            init_otel()
            self._tracer = trace.get_tracer("aspera.engine")
            self._meter = metrics.get_meter("aspera.engine")
            self._obs_step = self._meter.create_counter("aspera_observe_total")
            self._step_counter = self._meter.create_counter("aspera_step_total")
            self._decide_counter = self._meter.create_counter("aspera_decide_total")
        except Exception:
            self._tracer = None
            self._meter = None
            self._obs_step = None
            self._step_counter = None
            self._decide_counter = None

    def load_ast(self, ast: Dict[str, Any]):
        """
        Carica un AST Aspera.

        Args:
            ast: AST dictionary (output del parser)
        """
        self.ast = ast
        nodes = ast.get("nodes", [])

        # Estrai nodi per tipo
        for node in nodes:
            node_type = node.get("type")

            if node_type == "concept":
                name = node["name"]
                baseline = node.get("baseline", 0.5)
                self.concepts[name] = baseline
                logger.debug(f"Loaded concept: {name} (baseline={baseline})")

            elif node_type == "associate":
                self.associations.append(node)
                logger.debug(f"Loaded association: {node['from_concept']} -> {node['to_concept']}")

            elif node_type == "state":
                self.state = node.get("entries", {})
                logger.debug(f"Loaded state: {len(self.state)} entries")

            elif node_type == "inference":
                self.inferences.append(node)
                logger.debug(f"Loaded inference: {node['name']}")

            elif node_type == "intention":
                self.intentions.append(node)
                logger.debug(f"Loaded intention: {node['name']}")

            elif node_type == "explain":
                self.explain_config = node
                logger.debug("Loaded explain config")

        logger.info(f"AST loaded: {len(self.concepts)} concepts, {len(self.inferences)} inferences, {len(self.intentions)} intentions")

    def observe(self, signals: Dict[str, Any], context: Dict[str, Any] = None):
        """
        Registra nuova osservazione (signals esterni).

        Args:
            signals: Segnali di input
            context: Contesto aggiuntivo (experiences, etc.)
        """
        experiences = context.get("experiences", {}) if context else {}

        t0 = time.perf_counter()
        # Carica contesto nel symbolic reasoner
        self.symbolic_reasoner.load_context(
            signals=signals,
            state=self.state,
            concepts=self.concepts,
            experiences=experiences
        )

        # Memorizza episodio
        self.memory.store_episode(
            event_type="observation",
            data={"signals": signals, "context": context},
            importance=0.7,
            tags=["observation"]
        )

        logger.info(f"Observed signals: {list(signals.keys())}")
        try:
            if self._obs_step:
                self._obs_step.add(1)
        except Exception:
            pass
        self.metrics["durations"]["observe"] = round((time.perf_counter() - t0) * 1000, 2)

    def step(self) -> Dict[str, Any]:
        """
        Esegue un ciclo di ragionamento:
        1. Applica inferenze (simboliche e/o LLM)
        2. Aggiorna concetti e stato
        3. Propaga attivazioni tra concetti associati

        Returns:
            Risultato dello step con inferenze applicate
        """
        # Check resource limits
        self.resource_monitor.check_timeout()
        self.resource_monitor.check_memory()
        self.resource_monitor.record_inference_iteration()
        
        t0 = time.perf_counter()
        applied_inferences = []
        all_changes = []

        # Applica inferenze in due fasi per ridurre chiamate LLM:
        # 1) tutte le simboliche, 2) poi solo le LLM/hybrid usando lo stato aggiornato
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        symbolics = sorted([i for i in self.inferences if i.get("mode", "symbolic") == "symbolic"],
                           key=lambda i: priority_order.get(i.get("priority", "medium"), 2))
        non_symbolics = sorted([i for i in self.inferences if i.get("mode", "symbolic") != "symbolic"],
                               key=lambda i: priority_order.get(i.get("priority", "medium"), 2))

        # Passo 1: simboliche
        for inference in symbolics:
            when_ast = inference.get("when_ast")
            cond_ok = True
            if when_ast is not None:
                try:
                    cond_ok = bool(self.symbolic_reasoner.evaluate_expression(when_ast))
                except Exception:
                    cond_ok = False
            if not cond_ok:
                continue
            result = self.symbolic_reasoner.apply_inference(inference)
            if result:
                applied_inferences.append(result)
                all_changes.extend(result["changes"])

        # Passo 2: LLM/ibridi con stato aggiornato
        for inference in non_symbolics:
            mode = inference.get("mode", "symbolic")
            when_ast = inference.get("when_ast")
            cond_ok = True
            if when_ast is not None:
                try:
                    cond_ok = bool(self.symbolic_reasoner.evaluate_expression(when_ast))
                except Exception:
                    cond_ok = False
            if not cond_ok:
                continue
            if mode == "llm":
                try:
                    llm_result = self._apply_llm_inference(inference)
                    if llm_result:
                        applied_inferences.append(llm_result)
                        all_changes.extend(llm_result.get("changes", []))
                except Exception as e:
                    logger.error(f"LLM inference failed for {inference['name']}: {e}")
            elif mode == "hybrid":
                # Ripeti simbolico con stato aggiornato; fallback LLM se ancora senza effetto
                result = self.symbolic_reasoner.apply_inference(inference)
                if result:
                    applied_inferences.append(result)
                    all_changes.extend(result["changes"])
                else:
                    try:
                        llm_result = self._apply_llm_inference(inference)
                        if llm_result:
                            applied_inferences.append(llm_result)
                            all_changes.extend(llm_result.get("changes", []))
                    except Exception as e:
                        logger.error(f"Hybrid inference LLM fallback failed: {e}")

        # Propaga attivazioni tra concetti associati
        self._propagate_associations()

        # Aggiorna stato dall'updated context
        updated_context = self.symbolic_reasoner.get_context()
        self.concepts = updated_context["concept"]
        self.state = updated_context["state"]

        # Memorizza step
        self.memory.store_episode(
            event_type="reasoning_step",
            data={"applied_inferences": len(applied_inferences), "changes": all_changes},
            importance=0.8,
            tags=["reasoning"]
        )

        step_result = {
            "applied_inferences": applied_inferences,
            "changes": all_changes,
            "updated_concepts": self.concepts.copy(),
            "updated_state": self.state.copy()
        }

        self.execution_log.append({
            "phase": "step",
            "result": step_result
        })

        self.metrics["durations"]["step"] = round((time.perf_counter() - t0) * 1000, 2)
        try:
            if self._step_counter:
                self._step_counter.add(1)
        except Exception:
            pass
        logger.info(f"Step completed: {len(applied_inferences)} inferences applied, {len(all_changes)} changes")
        return step_result

    def decide(self) -> List[Dict[str, Any]]:
        """
        Esegue le intention strategies per decidere azioni.

        Returns:
            Lista di azioni selezionate
        """
        actions = self.policy_executor.execute_all_intentions(self.intentions)

        # Memorizza decisione
        self.memory.store_episode(
            event_type="decision",
            data={"actions": actions},
            importance=0.9,
            tags=["decision"]
        )

        self.execution_log.append({
            "phase": "decide",
            "actions": actions
        })

        self.metrics["counts"]["actions"] = len(actions)
        try:
            if self._decide_counter:
                self._decide_counter.add(1)
        except Exception:
            pass
        logger.info(f"Decision completed: {len(actions)} actions selected")
        return actions

    def explain(self, format: str = "human") -> str:
        """
        Genera spiegazione delle decisioni prese.

        Args:
            format: Formato spiegazione (human, formal, structured)

        Returns:
            Spiegazione testuale
        """
        t0 = time.perf_counter()
        if not self.explain_config:
            return "[No explanation template defined]"

        template = self.explain_config.get("template", "")
        max_words = self.explain_config.get("max_words", 40)
        tone = self.explain_config.get("tone", "neutral")

        # Raccogli osservazioni e inferenze recenti
        recent_episodes = self.memory.retrieve_episodes(limit=5)
        observation = {
            "signals": self.symbolic_reasoner.context.get("signals", {}),
            "concepts": self.concepts
        }
        inferences = [
            {"name": ep.data.get("applied_inferences", 0)}
            for ep in recent_episodes
            if ep.event_type == "reasoning_step"
        ]

        # Genera spiegazione con LLM
        try:
            explanation = self.llm.generate_explanation(
                template=template,
                observation=observation,
                inferences=inferences,
                max_words=max_words,
                tone=tone
            )
        except Exception as e:
            logger.error(f"Failed to generate explanation: {e}")
            explanation = f"[Error generating explanation: {e}]"

        # Memorizza
        self.memory.store_episode(
            event_type="explanation",
            data={"explanation": explanation, "format": format},
            importance=0.6,
            tags=["explanation"]
        )

        self.execution_log.append({
            "phase": "explain",
            "explanation": explanation
        })

        logger.info("Explanation generated")
        self.metrics["durations"]["explain"] = round((time.perf_counter() - t0) * 1000, 2)
        return explanation

    def _apply_llm_inference(self, inference: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Applica inferenza usando LLM"""
        inference_name = inference["name"]
        
        # Prepara contesto per LLM
        context = self.symbolic_reasoner.get_context()
        signals = context["signals"]
        rules = [f"{inference_name}: {inference.get('when_ast', '')}"]

        # Check cache first
        llm_result = None
        cache_key_prompt = f"inference:{inference_name}"
        cache_key_context = {"signals": signals, "state": self.state}
        
        if self.enable_cache and self.cache:
            cached_result = self.cache.get_llm_response(cache_key_prompt, cache_key_context)
            if cached_result is not None:
                llm_result = cached_result
                logger.debug(f"LLM cache HIT for {inference_name}")

        # Chiama LLM se non in cache
        if llm_result is None:
            # Track LLM usage (estimate ~500 tokens per call)
            self.resource_monitor.record_llm_call(tokens_used=500)

            @retry_with_backoff(max_retries=3, backoff_factor=2.0)
            def _do_call():
                return self.llm.generate_inference(context, signals, rules)

            try:
                llm_result = self._llm_cb.call(_do_call)
            except Exception as e:
                log_error_structured(e, {
                    "inference": inference_name,
                    "component": "LLM",
                })
                # Graceful degradation: no changes
                llm_result = {"changes": [], "notes": "LLM failed; degraded"}
            
            # Save to cache
            if self.enable_cache and self.cache:
                self.cache.cache_llm_response(cache_key_prompt, cache_key_context, llm_result)
                logger.debug(f"LLM cache MISS for {inference_name} - cached result")

        # Applica changes al contesto
        for change in llm_result.get("changes", []):
            concept_name = change.get("concept")
            delta = change.get("delta", 0)
            if concept_name in self.concepts:
                old_value = self.concepts[concept_name]
                new_value = max(0.0, min(1.0, old_value + delta))
                self.concepts[concept_name] = new_value
                logger.debug(f"LLM inference changed {concept_name}: {old_value} -> {new_value}")

        self.metrics["counts"]["applied_inferences"] += 1
        return {
            "inference_id": inference["id"],
            "inference_name": inference_name,
            "confidence": llm_result.get("confidence", 0.5),
            "mode": "llm",
            "changes": llm_result.get("changes", []),
            "rationale": llm_result.get("rationale", "")
        }

    def _propagate_associations(self):
        """Propaga attivazioni tra concetti associati"""
        for assoc in self.associations:
            from_concept = assoc["from_concept"]
            to_concept = assoc["to_concept"]
            weight = assoc.get("weight", 0.5)
            threshold = assoc.get("activation_threshold", 0.5)

            if from_concept in self.concepts and to_concept in self.concepts:
                from_value = self.concepts[from_concept]
                if from_value >= threshold:
                    # Propaga attivazione
                    delta = weight * (from_value - threshold) * 0.1
                    old_value = self.concepts[to_concept]
                    new_value = max(0.0, min(1.0, old_value + delta))
                    self.concepts[to_concept] = new_value
                    logger.debug(f"Association propagation: {from_concept} -> {to_concept} (delta={delta:.3f})")

    def get_state_snapshot(self) -> Dict[str, Any]:
        """Ritorna snapshot completo dello stato corrente"""
        snapshot = {
            "concepts": self.concepts.copy(),
            "state": self.state.copy(),
            "memory_stats": self.memory.get_stats(),
            "llm_stats": self.llm.get_stats(),
            "execution_log_length": len(self.execution_log),
            "metrics": self.metrics
        }
        
        # Add cache stats if enabled
        if self.enable_cache and self.cache:
            snapshot["cache_stats"] = self.cache.get_stats()
            snapshot["cache_performance"] = self.cache.get_performance_impact()
        
        return snapshot

    def get_audit_trail(self) -> Dict[str, Any]:
        """Ritorna trail completo per audit e debug"""
        return {
            "symbolic_audit": self.symbolic_reasoner.get_audit_log(),
            "policy_history": self.policy_executor.get_action_history(),
            "execution_log": self.execution_log,
            "memory_episodes": [ep.to_dict() for ep in self.memory.episodic_memory]
        }

    def export_state(self, filepath: str):
        """Esporta stato su file JSON"""
        import json
        state = {
            "snapshot": self.get_state_snapshot(),
            "audit_trail": self.get_audit_trail()
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)
        logger.info(f"State exported to {filepath}")

    def reset(self):
        """Reset completo del cognitive engine"""
        self.symbolic_reasoner.clear_audit_log()
        self.policy_executor.clear_history()
        self.memory.clear()
        self.execution_log = []
        logger.info("CognitiveEngine reset")

