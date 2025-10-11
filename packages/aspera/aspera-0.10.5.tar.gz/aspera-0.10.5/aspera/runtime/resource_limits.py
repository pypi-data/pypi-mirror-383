"""
ASPERA Runtime Resource Limits
===============================
Prevents runaway agents and ensures fair resource usage.

Features:
- CPU timeout per observation
- Memory usage cap
- Token budget tracking (LLM costs)
- Max iterations limit
- Configurable limits per agent/tier
- Real-time monitoring

Author: Christian Quintino De Luca - RTH Italia
Version: 0.1.0
"""

import time
import psutil
import threading
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum


class ResourceTier(Enum):
    """Resource allocation tiers"""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"
    UNLIMITED = "unlimited"  # For testing/dev


@dataclass
class ResourceLimits:
    """Resource limits configuration"""
    
    # CPU
    max_execution_time_seconds: float = 30.0  # Max time per observation
    
    # Memory
    max_memory_mb: Optional[float] = 500.0  # Max memory per agent
    
    # LLM
    max_tokens_per_observation: int = 10_000  # Max tokens per observation
    max_llm_calls_per_observation: int = 10  # Max LLM calls per observation
    # Cost
    cost_per_1k_tokens_usd: float = 0.0      # Cost per 1K tokens (set via config)
    max_cost_per_observation_usd: float = 999999.0  # Disable by default unless configured
    
    # Iterations
    max_inference_iterations: int = 100  # Max inference evaluation loops
    max_recursion_depth: int = 10  # Max recursive inference depth
    
    # Rate limiting (future)
    max_observations_per_minute: int = 60
    max_observations_per_hour: int = 1000
    
    @staticmethod
    def for_tier(tier: ResourceTier) -> 'ResourceLimits':
        """Get limits for a specific tier"""
        if tier == ResourceTier.FREE:
            return ResourceLimits(
                max_execution_time_seconds=5.0,
                max_memory_mb=100.0,
                max_tokens_per_observation=1_000,
                max_llm_calls_per_observation=3,
                max_inference_iterations=50,
                max_observations_per_minute=10,
                max_observations_per_hour=100
            )
        elif tier == ResourceTier.PRO:
            return ResourceLimits(
                max_execution_time_seconds=30.0,
                max_memory_mb=500.0,
                max_tokens_per_observation=10_000,
                max_llm_calls_per_observation=10,
                max_inference_iterations=100,
                max_observations_per_minute=60,
                max_observations_per_hour=1_000
            )
        elif tier == ResourceTier.ENTERPRISE:
            return ResourceLimits(
                max_execution_time_seconds=120.0,
                max_memory_mb=2_000.0,
                max_tokens_per_observation=100_000,
                max_llm_calls_per_observation=50,
                max_inference_iterations=500,
                max_observations_per_minute=300,
                max_observations_per_hour=10_000
            )
        elif tier == ResourceTier.UNLIMITED:
            return ResourceLimits(
                max_execution_time_seconds=float('inf'),
                max_memory_mb=None,
                max_tokens_per_observation=1_000_000,
                max_llm_calls_per_observation=1_000,
                max_inference_iterations=10_000,
                max_observations_per_minute=10_000,
                max_observations_per_hour=100_000
            )
        else:
            return ResourceLimits()  # Default (PRO-like)


class ResourceLimitExceeded(Exception):
    """Raised when a resource limit is exceeded"""
    
    def __init__(self, resource: str, limit: Any, actual: Any, message: str = None):
        self.resource = resource
        self.limit = limit
        self.actual = actual
        if message is None:
            message = f"Resource limit exceeded: {resource} (limit: {limit}, actual: {actual})"
        super().__init__(message)


class ResourceMonitor:
    """Monitor and enforce resource limits during execution"""
    
    def __init__(self, limits: ResourceLimits):
        self.limits = limits
        self.reset()
    
    def reset(self):
        """Reset monitoring counters for new observation"""
        self.start_time = time.time()
        self.initial_memory_mb = self._get_memory_usage_mb()
        self.token_count = 0
        self.llm_call_count = 0
        self.inference_iteration_count = 0
        self.recursion_depth = 0
        self.timeout_occurred = False
        self._timeout_thread = None
    
    def check_timeout(self) -> None:
        """Check if execution time limit exceeded"""
        elapsed = time.time() - self.start_time
        if elapsed > self.limits.max_execution_time_seconds:
            raise ResourceLimitExceeded(
                "execution_time",
                self.limits.max_execution_time_seconds,
                elapsed,
                f"Execution timeout: {elapsed:.2f}s > {self.limits.max_execution_time_seconds}s"
            )
    
    def check_memory(self) -> None:
        """Check if memory usage limit exceeded"""
        if self.limits.max_memory_mb is None:
            return
        
        current_memory = self._get_memory_usage_mb()
        memory_used = current_memory - self.initial_memory_mb
        
        if memory_used > self.limits.max_memory_mb:
            raise ResourceLimitExceeded(
                "memory",
                self.limits.max_memory_mb,
                memory_used,
                f"Memory limit exceeded: {memory_used:.2f}MB > {self.limits.max_memory_mb}MB"
            )
    
    def record_llm_call(self, tokens_used: int) -> None:
        """Record an LLM call and check limits"""
        self.llm_call_count += 1
        self.token_count += tokens_used
        
        if self.llm_call_count > self.limits.max_llm_calls_per_observation:
            raise ResourceLimitExceeded(
                "llm_calls",
                self.limits.max_llm_calls_per_observation,
                self.llm_call_count,
                f"LLM call limit exceeded: {self.llm_call_count} > {self.limits.max_llm_calls_per_observation}"
            )
        
        if self.token_count > self.limits.max_tokens_per_observation:
            raise ResourceLimitExceeded(
                "tokens",
                self.limits.max_tokens_per_observation,
                self.token_count,
                f"Token limit exceeded: {self.token_count} > {self.limits.max_tokens_per_observation}"
            )
        # Cost check (if configured)
        if self.limits.cost_per_1k_tokens_usd > 0 and self.limits.max_cost_per_observation_usd < 999999.0:
            est_cost = (self.token_count / 1000.0) * self.limits.cost_per_1k_tokens_usd
            if est_cost > self.limits.max_cost_per_observation_usd:
                raise ResourceLimitExceeded(
                    "llm_cost_usd",
                    self.limits.max_cost_per_observation_usd,
                    round(est_cost, 4),
                    f"LLM cost limit exceeded: ${est_cost:.4f} > ${self.limits.max_cost_per_observation_usd:.2f}"
                )
    
    def record_inference_iteration(self) -> None:
        """Record an inference evaluation iteration"""
        self.inference_iteration_count += 1
        
        if self.inference_iteration_count > self.limits.max_inference_iterations:
            raise ResourceLimitExceeded(
                "inference_iterations",
                self.limits.max_inference_iterations,
                self.inference_iteration_count,
                f"Inference iteration limit exceeded: {self.inference_iteration_count} > {self.limits.max_inference_iterations}"
            )
    
    def enter_recursion(self) -> None:
        """Enter a recursive inference call"""
        self.recursion_depth += 1
        
        if self.recursion_depth > self.limits.max_recursion_depth:
            raise ResourceLimitExceeded(
                "recursion_depth",
                self.limits.max_recursion_depth,
                self.recursion_depth,
                f"Recursion depth exceeded: {self.recursion_depth} > {self.limits.max_recursion_depth}"
            )
    
    def exit_recursion(self) -> None:
        """Exit a recursive inference call"""
        self.recursion_depth = max(0, self.recursion_depth - 1)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current resource usage stats"""
        elapsed = time.time() - self.start_time
        memory_used = self._get_memory_usage_mb() - self.initial_memory_mb
        
        return {
            "execution_time_seconds": elapsed,
            "memory_used_mb": memory_used,
            "token_count": self.token_count,
            "llm_call_count": self.llm_call_count,
            "inference_iteration_count": self.inference_iteration_count,
            "recursion_depth": self.recursion_depth,
            "limits": {
                "max_execution_time_seconds": self.limits.max_execution_time_seconds,
                "max_memory_mb": self.limits.max_memory_mb,
                "max_tokens_per_observation": self.limits.max_tokens_per_observation,
                "max_llm_calls_per_observation": self.limits.max_llm_calls_per_observation,
                "max_inference_iterations": self.limits.max_inference_iterations,
                "max_recursion_depth": self.limits.max_recursion_depth
            }
        }
    
    def start_timeout_monitor(self, callback: Optional[Callable] = None):
        """Start background thread to monitor timeout"""
        def monitor():
            time.sleep(self.limits.max_execution_time_seconds)
            self.timeout_occurred = True
            if callback:
                callback()
        
        self._timeout_thread = threading.Thread(target=monitor, daemon=True)
        self._timeout_thread.start()
    
    def stop_timeout_monitor(self):
        """Stop timeout monitoring thread"""
        if self._timeout_thread:
            # Thread will exit naturally when observation completes
            self._timeout_thread = None
    
    def _get_memory_usage_mb(self) -> float:
        """Get current process memory usage in MB"""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # Convert bytes to MB
        except:
            return 0.0


class ResourceGuard:
    """
    Context manager for resource-limited execution.
    
    Usage:
        limits = ResourceLimits.for_tier(ResourceTier.FREE)
        with ResourceGuard(limits) as monitor:
            # Execute code
            monitor.check_timeout()
            monitor.check_memory()
            result = some_computation()
    """
    
    def __init__(self, limits: ResourceLimits):
        self.monitor = ResourceMonitor(limits)
    
    def __enter__(self) -> ResourceMonitor:
        """Enter resource-guarded context"""
        self.monitor.reset()
        return self.monitor
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit resource-guarded context"""
        self.monitor.stop_timeout_monitor()
        
        # Don't suppress exceptions
        return False


# Convenience functions

def create_monitor(tier: ResourceTier = ResourceTier.PRO) -> ResourceMonitor:
    """Create a resource monitor for a specific tier"""
    limits = ResourceLimits.for_tier(tier)
    return ResourceMonitor(limits)


def with_limits(tier: ResourceTier = ResourceTier.PRO):
    """Decorator for resource-limited functions"""
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            limits = ResourceLimits.for_tier(tier)
            with ResourceGuard(limits) as monitor:
                # Inject monitor as keyword argument if function accepts it
                import inspect
                sig = inspect.signature(func)
                if 'resource_monitor' in sig.parameters:
                    kwargs['resource_monitor'] = monitor
                
                return func(*args, **kwargs)
        
        return wrapper
    return decorator

