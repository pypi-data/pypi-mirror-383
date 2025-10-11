"""Ollama Local Models Adapter"""
from typing import Any, Dict, List, Optional

class OllamaAdapter:
    def __init__(self, model: str = "llama3.2", base_url: str = "http://localhost:11434"):
        try:
            import ollama
            self.client = ollama.Client(host=base_url)
        except ImportError:
            raise ImportError("ollama package required: pip install ollama")
        self.model = model
        self.stats = {"total_calls": 0}
    
    def generate_inference(self, context: Dict[str, Any], signals: Dict[str, Any], rules: List[str]) -> Dict[str, Any]:
        self.stats["total_calls"] += 1
        prompt = f"Context: {context}\nSignals: {signals}\nRules: {rules}"
        try:
            response = self.client.generate(model=self.model, prompt=prompt)
            return {"changes": [], "confidence": 0.7, "reasoning": response['response']}
        except Exception as e:
            return {"changes": [], "confidence": 0.5, "reasoning": f"Error: {e}"}
    
    def get_stats(self) -> Dict[str, Any]:
        return self.stats.copy()

