"""
Enterprise Error Handling for ASPERA
=====================================

Production-grade error handling with:
- Circuit Breaker pattern
- Exponential backoff retry
- Graceful degradation
- Structured logging
- Error metrics tracking

Author: Christian Quintino De Luca - RTH Italia
License: MIT
"""
import time
import logging
from typing import Any, Callable, Optional, Dict
from functools import wraps
from datetime import datetime
from collections import defaultdict

# Structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ErrorMetrics:
    """Track error metrics for monitoring."""
    
    def __init__(self):
        self.errors = defaultdict(int)
        self.total_errors = 0
        self.last_error_time = None
        self.error_history = []
    
    def record_error(self, error_type: str, error_msg: str):
        """Record an error occurrence."""
        self.errors[error_type] += 1
        self.total_errors += 1
        self.last_error_time = datetime.now()
        self.error_history.append({
            "timestamp": self.last_error_time.isoformat(),
            "type": error_type,
            "message": error_msg
        })
        # Keep only last 100 errors
        if len(self.error_history) > 100:
            self.error_history.pop(0)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get error statistics."""
        return {
            "total_errors": self.total_errors,
            "errors_by_type": dict(self.errors),
            "last_error": self.last_error_time.isoformat() if self.last_error_time else None,
            "recent_errors": self.error_history[-10:]  # Last 10
        }
    
    def reset(self):
        """Reset metrics."""
        self.errors.clear()
        self.total_errors = 0
        self.last_error_time = None
        self.error_history.clear()


# Global metrics instance
_error_metrics = ErrorMetrics()


def get_error_metrics() -> ErrorMetrics:
    """Get global error metrics."""
    return _error_metrics

class CircuitBreaker:
    """
    Circuit Breaker pattern for LLM calls.
    
    States:
    - CLOSED: Normal operation
    - OPEN: Too many failures, reject all calls
    - HALF_OPEN: Testing if service recovered
    
    Example:
        cb = CircuitBreaker(failure_threshold=5, timeout=60)
        result = cb.call(expensive_llm_call, arg1, arg2)
    """
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60, name: str = "default"):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.name = name
        self.failures = 0
        self.successes = 0
        self.last_failure_time = None
        self.last_success_time = None
        self.state = "closed"  # closed, open, half_open
        logger.info(f"CircuitBreaker '{name}' initialized (threshold={failure_threshold}, timeout={timeout}s)")
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        if self.state == "open":
            if time.time() - self.last_failure_time > self.timeout:
                logger.info(f"CircuitBreaker '{self.name}': Transitioning to HALF_OPEN (timeout expired)")
                self.state = "half_open"
            else:
                error_msg = f"Circuit breaker '{self.name}' is OPEN (too many failures)"
                _error_metrics.record_error("CircuitBreakerOpen", error_msg)
                raise CircuitBreakerOpenError(error_msg)
        
        try:
            result = func(*args, **kwargs)
            
            # Success - update state
            self.successes += 1
            self.last_success_time = time.time()
            
            if self.state == "half_open":
                logger.info(f"CircuitBreaker '{self.name}': Success in HALF_OPEN, transitioning to CLOSED")
                self.state = "closed"
                self.failures = 0
            
            return result
            
        except Exception as e:
            # Failure - update state
            self.failures += 1
            self.last_failure_time = time.time()
            
            error_type = type(e).__name__
            _error_metrics.record_error(f"CircuitBreaker_{self.name}_{error_type}", str(e))
            
            if self.failures >= self.failure_threshold:
                logger.error(f"CircuitBreaker '{self.name}': Opening circuit ({self.failures} failures >= {self.failure_threshold})")
                self.state = "open"
            
            raise e
    
    def reset(self):
        """Manually reset circuit breaker."""
        logger.info(f"CircuitBreaker '{self.name}': Manual reset")
        self.state = "closed"
        self.failures = 0
        self.successes = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics."""
        return {
            "name": self.name,
            "state": self.state,
            "failures": self.failures,
            "successes": self.successes,
            "failure_threshold": self.failure_threshold,
            "timeout": self.timeout,
            "last_failure": self.last_failure_time,
            "last_success": self.last_success_time
        }


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""
    pass

def retry_with_backoff(
    max_retries: int = 3,
    backoff_factor: float = 2.0,
    max_wait: float = 60.0,
    exceptions: tuple = (Exception,)
):
    """
    Retry decorator with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Multiplier for wait time (exponential)
        max_wait: Maximum wait time between retries (cap)
        exceptions: Tuple of exceptions to catch and retry
    
    Example:
        @retry_with_backoff(max_retries=5, backoff_factor=2.0)
        def unreliable_api_call():
            return requests.get("https://api.example.com/")
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                    
                except exceptions as e:
                    if attempt == max_retries - 1:
                        # Last attempt failed, give up
                        error_msg = f"{func.__name__} failed after {max_retries} retries"
                        _error_metrics.record_error("RetryExhausted", error_msg)
                        logger.error(error_msg)
                        raise
                    
                    # Calculate wait time with exponential backoff
                    wait_time = min(backoff_factor ** attempt, max_wait)
                    
                    logger.warning(
                        f"{func.__name__} failed (attempt {attempt+1}/{max_retries}): {e}. "
                        f"Retrying in {wait_time:.1f}s..."
                    )
                    _error_metrics.record_error(f"Retry_{type(e).__name__}", str(e))
                    
                    time.sleep(wait_time)
            
        return wrapper
    return decorator


class GracefulDegradation:
    """
    Fallback mechanisms for failures.
    
    Provides multiple strategies for handling failures:
    - LLM fallback (primary → fallback LLM)
    - Symbolic fallback (LLM → symbolic rules)
    - Default value on error
    - Cached result on error
    """
    
    @staticmethod
    def llm_fallback_chain(fallback_chain: list):
        """
        Try LLMs in order until one succeeds.
        
        Args:
            fallback_chain: List of LLM adapters to try
        
        Example:
            @GracefulDegradation.llm_fallback_chain([groq, openai, anthropic])
            def generate_text(prompt, llm):
                return llm.infer(prompt)
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                last_error = None
                
                for i, llm in enumerate(fallback_chain):
                    try:
                        logger.info(f"Trying LLM {i+1}/{len(fallback_chain)}: {llm.__class__.__name__}")
                        return func(*args, **kwargs, llm=llm)
                        
                    except Exception as e:
                        last_error = e
                        logger.warning(f"LLM {llm.__class__.__name__} failed: {e}")
                        _error_metrics.record_error(f"LLMFallback_{llm.__class__.__name__}", str(e))
                        
                        if i < len(fallback_chain) - 1:
                            continue  # Try next LLM
                
                # All LLMs failed
                error_msg = f"All {len(fallback_chain)} LLMs failed"
                _error_metrics.record_error("AllLLMsFailed", error_msg)
                raise Exception(error_msg) from last_error
                
            return wrapper
        return decorator
    
    @staticmethod
    def symbolic_fallback(symbolic_func: Callable):
        """
        Fallback to symbolic reasoning if LLM fails.
        
        Example:
            @GracefulDegradation.symbolic_fallback(symbolic_classifier)
            def classify_with_llm(text):
                return llm.classify(text)
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"LLM failed: {e}, falling back to symbolic reasoning")
                    _error_metrics.record_error("LLM_to_Symbolic_Fallback", str(e))
                    return symbolic_func(*args, **kwargs)
            return wrapper
        return decorator
    
    @staticmethod
    def default_on_error(default_value: Any, log_error: bool = True):
        """
        Return default value on error.
        
        Args:
            default_value: Value to return if function fails
            log_error: Whether to log the error
        
        Example:
            @GracefulDegradation.default_on_error(default_value={"status": "unknown"})
            def risky_operation():
                return potentially_failing_api_call()
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if log_error:
                        logger.error(f"Error in {func.__name__}: {e}, returning default value")
                    _error_metrics.record_error(f"DefaultOnError_{func.__name__}", str(e))
                    return default_value
            return wrapper
        return decorator
    
    @staticmethod
    def cached_on_error(cache: Dict[str, Any], cache_key_func: Callable):
        """
        Return cached result on error.
        
        Args:
            cache: Dictionary to use as cache
            cache_key_func: Function to generate cache key from args
        
        Example:
            my_cache = {}
            @GracefulDegradation.cached_on_error(my_cache, lambda x: x)
            def fetch_data(user_id):
                return api.get_user(user_id)
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cache_key = cache_key_func(*args, **kwargs)
                
                try:
                    result = func(*args, **kwargs)
                    # Update cache on success
                    cache[cache_key] = result
                    return result
                    
                except Exception as e:
                    # Try to use cached value
                    if cache_key in cache:
                        logger.warning(f"{func.__name__} failed: {e}, using cached result")
                        _error_metrics.record_error(f"UsedCache_{func.__name__}", str(e))
                        return cache[cache_key]
                    else:
                        logger.error(f"{func.__name__} failed and no cache available")
                        raise
                        
            return wrapper
        return decorator


# Helper function for structured error logging
def log_error_structured(
    error: Exception,
    context: Dict[str, Any],
    severity: str = "ERROR"
):
    """
    Log error with structured context.
    
    Args:
        error: Exception to log
        context: Additional context (user_id, request_id, etc.)
        severity: Error severity (ERROR, WARNING, CRITICAL)
    """
    error_data = {
        "timestamp": datetime.now().isoformat(),
        "severity": severity,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context
    }
    
    logger.error(f"Structured error: {error_data}")
    _error_metrics.record_error(type(error).__name__, str(error))
    
    return error_data

