"""
LLM Router - Automatically selects best LLM provider
"""
import os
from typing import Any, Dict, List, Optional

class LLMRouter:
    """Intelligently routes LLM requests to best available provider"""
    
    PROVIDER_PRIORITY = ["groq", "openai", "anthropic", "gemini", "ollama"]
    PROVIDER_COSTS = {"groq": 0.001, "openai": 0.015, "anthropic": 0.015, "gemini": 0.001, "ollama": 0.0}
    
    def __init__(self, prefer_local: bool = False, max_cost_per_call: float = 0.01):
        self.prefer_local = prefer_local
        self.max_cost_per_call = max_cost_per_call
        self.available_providers = self._detect_available()
        self.active_adapter = None
        self.stats = {"total_calls": 0, "provider_usage": {}}
    
    def _detect_available(self) -> Dict[str, bool]:
        """Detect which LLM providers are available"""
        available = {}
        
        # Groq
        available["groq"] = bool(os.getenv("GROQ_API_KEY"))
        
        # OpenAI
        available["openai"] = bool(os.getenv("OPENAI_API_KEY"))
        
        # Anthropic
        available["anthropic"] = bool(os.getenv("ANTHROPIC_API_KEY"))
        
        # Gemini
        available["gemini"] = bool(os.getenv("GOOGLE_API_KEY"))
        
        # Ollama (check if service is running)
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=1)
            available["ollama"] = response.status_code == 200
        except:
            available["ollama"] = False
        
        return available
    
    def select_provider(self) -> str:
        """Select best provider based on availability, cost, and preferences"""
        if self.prefer_local and self.available_providers.get("ollama"):
            return "ollama"
        
        # Filter by cost and availability
        candidates = []
        for provider in self.PROVIDER_PRIORITY:
            if self.available_providers.get(provider):
                if self.PROVIDER_COSTS[provider] <= self.max_cost_per_call:
                    candidates.append(provider)
        
        return candidates[0] if candidates else "mock"
    
    def get_adapter(self):
        """Get LLM adapter for selected provider"""
        if self.active_adapter:
            return self.active_adapter
        
        provider = self.select_provider()
        
        if provider == "groq":
            from aspera.runtime.llm_adapters.groq_adapter import GroqAdapter
            self.active_adapter = GroqAdapter()
        elif provider == "openai":
            from aspera.runtime.llm_adapters.openai_adapter import OpenAIAdapter
            self.active_adapter = OpenAIAdapter()
        elif provider == "anthropic":
            from aspera.runtime.llm_adapters.anthropic_adapter import AnthropicAdapter
            self.active_adapter = AnthropicAdapter()
        elif provider == "gemini":
            from aspera.runtime.llm_adapters.gemini_adapter import GeminiAdapter
            self.active_adapter = GeminiAdapter()
        elif provider == "ollama":
            from aspera.runtime.llm_adapters.ollama_adapter import OllamaAdapter
            self.active_adapter = OllamaAdapter()
        else:
            from aspera.runtime.llm_adapters.groq_adapter import MockGroqAdapter
            self.active_adapter = MockGroqAdapter()
        
        return self.active_adapter
    
    def generate_inference(self, context: Dict[str, Any], signals: Dict[str, Any], rules: List[str]) -> Dict[str, Any]:
        """Generate inference using best available provider"""
        self.stats["total_calls"] += 1
        adapter = self.get_adapter()
        provider = self.select_provider()
        
        self.stats["provider_usage"][provider] = self.stats["provider_usage"].get(provider, 0) + 1
        
        return adapter.generate_inference(context, signals, rules)
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            **self.stats,
            "available_providers": self.available_providers,
            "active_provider": self.select_provider()
        }

