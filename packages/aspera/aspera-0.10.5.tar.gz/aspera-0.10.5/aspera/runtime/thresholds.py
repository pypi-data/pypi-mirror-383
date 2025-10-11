"""
Threshold Learning (Epsilon-Greedy)
===================================
Modulo per l'adattamento continuo di soglie simboliche basato su feedback.

- Mantiene una tabella di soglie per coppie (scope.key), es. (concept.cart_abandon_risk)
- Applica un semplice algoritmo epsilon-greedy per esplorare/raffinare la soglia
- Espone metodi per: get_threshold, record_feedback(success/failure), update

Note: implementazione stateless minimale; in produzione collegare a storage persistente.
"""

from __future__ import annotations

from typing import Dict, Tuple, Optional
import random
import time


class ThresholdBandit:
    """Epsilon-Greedy per una singola soglia continua in [0,1]."""

    def __init__(self, initial: float = 0.5, epsilon: float = 0.1, step: float = 0.02):
        self.value: float = max(0.0, min(1.0, initial))
        self.epsilon: float = max(0.0, min(1.0, epsilon))
        self.step: float = max(0.001, min(0.2, step))
        self.successes: int = 0
        self.failures: int = 0
        self.last_update_ts: float = time.time()

    def propose(self) -> float:
        # Epsilon: con probabilità epsilon, esplora +/- step
        if random.random() < self.epsilon:
            direction = 1 if random.random() < 0.5 else -1
            proposal = self.value + direction * self.step
            return max(0.0, min(1.0, proposal))
        return self.value

    def record(self, success: bool, observed_score: Optional[float] = None) -> None:
        if success:
            self.successes += 1
            # Muovi soglia verso proposal più stringente se troppo permissiva
            self.value = min(1.0, self.value + self.step / 2)
        else:
            self.failures += 1
            # Allenta soglia
            self.value = max(0.0, self.value - self.step)
        self.last_update_ts = time.time()

    def stats(self) -> Dict[str, float]:
        total = self.successes + self.failures
        cr = (self.successes / total) if total else 0.0
        return {
            "value": round(self.value, 4),
            "epsilon": round(self.epsilon, 3),
            "step": round(self.step, 3),
            "successes": self.successes,
            "failures": self.failures,
            "conversion_rate": round(cr, 4),
        }


class ThresholdRegistry:
    """Registro in-memory di bandit per chiave di soglia."""

    def __init__(self):
        self._store: Dict[str, ThresholdBandit] = {}

    def get(self, key: str, default: float = 0.5) -> ThresholdBandit:
        if key not in self._store:
            self._store[key] = ThresholdBandit(initial=default)
        return self._store[key]

    def get_value(self, key: str, default: float = 0.5) -> float:
        return self.get(key, default).propose()

    def record_feedback(self, key: str, success: bool, observed_score: Optional[float] = None) -> None:
        self.get(key).record(success, observed_score)

    def export(self) -> Dict[str, Dict[str, float]]:
        return {k: v.stats() for k, v in self._store.items()}


# Singleton semplice in runtime
_GLOBAL_THRESHOLDS: Optional[ThresholdRegistry] = None


def get_thresholds() -> ThresholdRegistry:
    global _GLOBAL_THRESHOLDS
    if _GLOBAL_THRESHOLDS is None:
        _GLOBAL_THRESHOLDS = ThresholdRegistry()
    return _GLOBAL_THRESHOLDS


