"""
OpenAI LLM Adapter for ASPERA
"""
import os
from typing import Any, Dict, List, Optional

class OpenAIAdapter:
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY required")
        
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("openai package required: pip install openai")
        
        self.model = model
        self.stats = {"total_calls": 0, "total_tokens": 0}
    
    def generate_inference(self, context: Dict[str, Any], signals: Dict[str, Any], rules: List[str]) -> Dict[str, Any]:
        self.stats["total_calls"] += 1
        prompt = f"Context: {context}\nSignals: {signals}\nRules: {rules}\nAnalyze and provide concept changes."
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=200
            )
            content = response.choices[0].message.content
            self.stats["total_tokens"] += response.usage.total_tokens
            return {"changes": [], "confidence": 0.7, "reasoning": content}
        except Exception as e:
            return {"changes": [], "confidence": 0.5, "reasoning": f"Error: {e}"}
    
    def get_stats(self) -> Dict[str, Any]:
        return self.stats.copy()

