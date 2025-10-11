"""
ASPERA Caching Layer
====================
Intelligent caching system for symbolic reasoning and LLM responses.
Reduces costs by 50%+ through smart memoization.

Author: Christian Quintino De Luca - RTH Italia
Version: 0.1.0
"""

import hashlib
import json
import time
from typing import Any, Dict, Optional, Tuple
from collections import OrderedDict
import threading


class CacheEntry:
    """Single cache entry with metadata"""
    
    def __init__(self, value: Any, ttl: Optional[float] = None):
        self.value = value
        self.created_at = time.time()
        self.last_accessed = time.time()
        self.access_count = 0
        self.ttl = ttl  # Time to live in seconds
        self.hits = 0
    
    def is_expired(self) -> bool:
        """Check if entry has expired"""
        if self.ttl is None:
            return False
        return (time.time() - self.created_at) > self.ttl
    
    def touch(self):
        """Update access time and count"""
        self.last_accessed = time.time()
        self.access_count += 1
        self.hits += 1


class LRUCache:
    """Thread-safe LRU cache with TTL support"""
    
    def __init__(self, max_size: int = 1000, default_ttl: Optional[float] = None):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.lock = threading.RLock()
        
        # Statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "expirations": 0,
            "total_requests": 0
        }
    
    def _hash_key(self, key: Any) -> str:
        """Generate stable hash for any key"""
        if isinstance(key, str):
            return key
        
        # Convert to stable JSON string
        key_str = json.dumps(key, sort_keys=True, default=str)
        return hashlib.sha256(key_str.encode()).hexdigest()
    
    def get(self, key: Any) -> Optional[Any]:
        """Get value from cache"""
        with self.lock:
            self.stats["total_requests"] += 1
            hash_key = self._hash_key(key)
            
            if hash_key not in self.cache:
                self.stats["misses"] += 1
                return None
            
            entry = self.cache[hash_key]
            
            # Check expiration
            if entry.is_expired():
                self.stats["expirations"] += 1
                self.stats["misses"] += 1
                del self.cache[hash_key]
                return None
            
            # Update access and move to end (most recently used)
            entry.touch()
            self.cache.move_to_end(hash_key)
            self.stats["hits"] += 1
            
            return entry.value
    
    def set(self, key: Any, value: Any, ttl: Optional[float] = None):
        """Set value in cache"""
        with self.lock:
            hash_key = self._hash_key(key)
            
            # Remove if exists
            if hash_key in self.cache:
                del self.cache[hash_key]
            
            # Evict oldest if at capacity
            if len(self.cache) >= self.max_size:
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
                self.stats["evictions"] += 1
            
            # Add new entry
            entry_ttl = ttl if ttl is not None else self.default_ttl
            self.cache[hash_key] = CacheEntry(value, entry_ttl)
    
    def clear(self):
        """Clear entire cache"""
        with self.lock:
            self.cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            total = self.stats["total_requests"]
            hit_rate = (self.stats["hits"] / total * 100) if total > 0 else 0
            
            return {
                **self.stats,
                "size": len(self.cache),
                "max_size": self.max_size,
                "hit_rate": f"{hit_rate:.2f}%",
                "miss_rate": f"{100 - hit_rate:.2f}%"
            }
    
    def __len__(self) -> int:
        return len(self.cache)


class AsperaCache:
    """
    Multi-layer caching system for ASPERA runtime.
    
    Layers:
    1. Symbolic reasoning cache (no TTL, deterministic)
    2. LLM response cache (TTL 1 hour, expensive calls)
    3. Concept evaluation cache (TTL 5 min, dynamic)
    """
    
    def __init__(
        self,
        symbolic_cache_size: int = 5000,
        llm_cache_size: int = 1000,
        concept_cache_size: int = 2000,
        enable_llm_cache: bool = True
    ):
        # Layer 1: Symbolic reasoning (deterministic, no TTL)
        self.symbolic_cache = LRUCache(
            max_size=symbolic_cache_size,
            default_ttl=None  # Never expires (deterministic)
        )
        
        # Layer 2: LLM responses (expensive, TTL 1 hour)
        self.llm_cache = LRUCache(
            max_size=llm_cache_size,
            default_ttl=3600 if enable_llm_cache else 0  # 1 hour
        )
        self.enable_llm_cache = enable_llm_cache
        
        # Layer 3: Concept evaluations (dynamic, TTL 5 min)
        self.concept_cache = LRUCache(
            max_size=concept_cache_size,
            default_ttl=300  # 5 minutes
        )
    
    def cache_symbolic_result(
        self,
        condition: Dict[str, Any],
        state: Dict[str, Any],
        result: Any
    ):
        """Cache symbolic reasoning result"""
        key = {
            "type": "symbolic",
            "condition": condition,
            "state": state
        }
        self.symbolic_cache.set(key, result)
    
    def get_symbolic_result(
        self,
        condition: Dict[str, Any],
        state: Dict[str, Any]
    ) -> Optional[Any]:
        """Get cached symbolic reasoning result"""
        key = {
            "type": "symbolic",
            "condition": condition,
            "state": state
        }
        return self.symbolic_cache.get(key)
    
    def cache_llm_response(
        self,
        prompt: str,
        context: Dict[str, Any],
        response: str,
        ttl: Optional[float] = None
    ):
        """Cache LLM response"""
        if not self.enable_llm_cache:
            return
        
        key = {
            "type": "llm",
            "prompt": prompt,
            "context": context
        }
        self.llm_cache.set(key, response, ttl)
    
    def get_llm_response(
        self,
        prompt: str,
        context: Dict[str, Any]
    ) -> Optional[str]:
        """Get cached LLM response"""
        if not self.enable_llm_cache:
            return None
        
        key = {
            "type": "llm",
            "prompt": prompt,
            "context": context
        }
        return self.llm_cache.get(key)
    
    def cache_concept_value(
        self,
        concept_name: str,
        signals: Dict[str, float],
        value: float,
        ttl: Optional[float] = None
    ):
        """Cache concept evaluation"""
        key = {
            "type": "concept",
            "name": concept_name,
            "signals": signals
        }
        self.concept_cache.set(key, value, ttl)
    
    def get_concept_value(
        self,
        concept_name: str,
        signals: Dict[str, float]
    ) -> Optional[float]:
        """Get cached concept evaluation"""
        key = {
            "type": "concept",
            "name": concept_name,
            "signals": signals
        }
        return self.concept_cache.get(key)
    
    def clear_all(self):
        """Clear all cache layers"""
        self.symbolic_cache.clear()
        self.llm_cache.clear()
        self.concept_cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        return {
            "symbolic": self.symbolic_cache.get_stats(),
            "llm": self.llm_cache.get_stats(),
            "concept": self.concept_cache.get_stats(),
            "total_size": (
                len(self.symbolic_cache) +
                len(self.llm_cache) +
                len(self.concept_cache)
            )
        }
    
    def get_performance_impact(self) -> Dict[str, Any]:
        """Calculate performance impact of caching"""
        symbolic_stats = self.symbolic_cache.get_stats()
        llm_stats = self.llm_cache.get_stats()
        
        # Estimate cost savings (assuming $0.002 per LLM call)
        llm_hits = llm_stats["hits"]
        estimated_savings = llm_hits * 0.002
        
        # Estimate latency reduction (assuming 1s per LLM call, 0.01s per symbolic)
        symbolic_hits = symbolic_stats["hits"]
        time_saved = (llm_hits * 1.0) + (symbolic_hits * 0.01)
        
        return {
            "estimated_cost_savings_usd": f"${estimated_savings:.4f}",
            "estimated_time_saved_seconds": f"{time_saved:.2f}s",
            "llm_calls_avoided": llm_hits,
            "symbolic_recalculations_avoided": symbolic_hits
        }


# Global cache instance (singleton)
_global_cache: Optional[AsperaCache] = None


def get_cache(
    symbolic_cache_size: int = 5000,
    llm_cache_size: int = 1000,
    concept_cache_size: int = 2000,
    enable_llm_cache: bool = True
) -> AsperaCache:
    """Get or create global cache instance"""
    global _global_cache
    if _global_cache is None:
        _global_cache = AsperaCache(
            symbolic_cache_size=symbolic_cache_size,
            llm_cache_size=llm_cache_size,
            concept_cache_size=concept_cache_size,
            enable_llm_cache=enable_llm_cache
        )
    return _global_cache


def reset_cache():
    """Reset global cache (useful for testing)"""
    global _global_cache
    if _global_cache is not None:
        _global_cache.clear_all()
    _global_cache = None

