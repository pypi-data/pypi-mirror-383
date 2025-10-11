"""
HuggingFace Inference API adapter for ASPERA.

Provides free access to open-source models via HuggingFace API.
Free tier: 30,000 requests/month, 100 requests/minute.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
import requests

logger = logging.getLogger(__name__)


class HuggingFaceAdapter:
    """
    Adapter for HuggingFace Inference API.
    
    Free Models Available (NO gating, NO approval needed):
    - flan-t5: Google Flan-T5 Base (250M) - Recommended! Fast & reliable
    - bloom: BigScience BLOOM (560M) - Multilingual, good quality
    - dialogpt: Microsoft DialoGPT (345M) - Best for conversations
    - gpt-neo: EleutherAI GPT-Neo (125M) - Good general purpose
    - gpt2: OpenAI GPT-2 (124M) - Classic, always works
    - distilgpt2: DistilGPT2 (82M) - Fastest
    - opt: Meta OPT (125M) - Good quality
    
    Usage:
        adapter = HuggingFaceAdapter(
            api_key="hf_...",  # Get free at https://huggingface.co/settings/tokens
            model="flan-t5"  # or "bloom", "dialogpt", etc.
        )
    """
    
    DEFAULT_MODELS = {
        # Models that work 100% FREE with Inference API (no gating, no approval)
        "flan-t5": "google/flan-t5-base",  # 250M - Fast, reliable
        "gpt2": "gpt2",  # 124M - Classic, always works
        "gpt-neo": "EleutherAI/gpt-neo-125m",  # 125M - Good quality
        "distilgpt2": "distilgpt2",  # 82M - Fastest
        "bloom": "bigscience/bloomz-560m",  # 560M - Multilingual
        "opt": "facebook/opt-125m",  # 125M - Meta's model
        "dialogpt": "microsoft/DialoGPT-medium"  # 345M - Conversational
    }
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "flan-t5",  # Default to flan-t5 (works 100% free, no gating)
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize HuggingFace adapter.
        
        Args:
            api_key: HuggingFace API token (or set HF_API_KEY env var)
            model: Model shorthand (flan-t5, bloom, dialogpt, gpt-neo, gpt2, distilgpt2, opt)
            timeout: Request timeout in seconds
            max_retries: Max retry attempts
        """
        self.api_key = api_key or os.environ.get("HF_API_KEY") or os.environ.get("HUGGINGFACE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "HuggingFace API key required. Get free key at: "
                "https://huggingface.co/settings/tokens\n"
                "Set via HF_API_KEY environment variable or pass to constructor."
            )
        
        # Resolve model shorthand
        self.model = self.DEFAULT_MODELS.get(model, model)
        self.timeout = timeout
        self.max_retries = max_retries
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model}"
        
        logger.info(f"Initialized HuggingFace adapter with model: {self.model}")
    
    def query(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
        **kwargs
    ) -> str:
        """
        Query HuggingFace model.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)
            top_p: Nucleus sampling parameter
            **kwargs: Additional model parameters
            
        Returns:
            Generated text response
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "return_full_text": False,
                **kwargs
            }
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )
                
                if response.status_code == 503:
                    # Model is loading, wait and retry
                    wait_time = min(2 ** attempt, 10)
                    logger.warning(f"Model loading, waiting {wait_time}s... (attempt {attempt + 1}/{self.max_retries})")
                    import time
                    time.sleep(wait_time)
                    continue
                
                response.raise_for_status()
                
                result = response.json()
                
                # Handle different response formats
                if isinstance(result, list) and len(result) > 0:
                    if isinstance(result[0], dict) and "generated_text" in result[0]:
                        return result[0]["generated_text"].strip()
                    elif isinstance(result[0], str):
                        return result[0].strip()
                elif isinstance(result, dict) and "generated_text" in result:
                    return result["generated_text"].strip()
                elif isinstance(result, str):
                    return result.strip()
                else:
                    logger.warning(f"Unexpected response format: {result}")
                    return str(result)
                    
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    logger.error("Rate limit exceeded. Free tier: 100 req/min, 30k/month")
                    raise ValueError("HuggingFace rate limit exceeded. Wait a minute or upgrade.")
                elif e.response.status_code == 401:
                    raise ValueError("Invalid HuggingFace API key. Get free key at: https://huggingface.co/settings/tokens")
                else:
                    logger.error(f"HuggingFace API error: {e.response.status_code} - {e.response.text}")
                    if attempt == self.max_retries - 1:
                        raise
            except Exception as e:
                logger.error(f"HuggingFace request failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt == self.max_retries - 1:
                    raise
        
        raise RuntimeError(f"Failed to get response from HuggingFace after {self.max_retries} attempts")
    
    def infer(self, prompt: str, context: Dict[str, Any]) -> str:
        """
        ASPERA-compatible inference method.
        
        Args:
            prompt: LLM prompt
            context: Cognitive context (signals, concepts, memory)
            
        Returns:
            LLM response text
        """
        # Build rich prompt with context
        full_prompt = self._build_prompt(prompt, context)
        
        try:
            response = self.query(full_prompt)
            logger.info(f"HuggingFace inference successful (model: {self.model})")
            return response
        except Exception as e:
            logger.error(f"HuggingFace inference failed: {e}")
            raise
    
    def _build_prompt(self, prompt: str, context: Dict[str, Any]) -> str:
        """Build enhanced prompt with cognitive context."""
        parts = []
        
        # Add system context
        parts.append("You are ASPERA, a hybrid cognitive AI system.")
        
        # Add signals if available
        if "signals" in context and context["signals"]:
            signals_str = ", ".join([f"{k}={v}" for k, v in context["signals"].items()])
            parts.append(f"Current signals: {signals_str}")
        
        # Add active concepts if available
        if "concepts" in context and context["concepts"]:
            concepts_str = ", ".join([f"{k}={v:.2f}" for k, v in context["concepts"].items() if v > 0.5])
            if concepts_str:
                parts.append(f"Active concepts: {concepts_str}")
        
        # Add main prompt
        parts.append(f"\n{prompt}")
        
        return "\n".join(parts)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about current model."""
        return {
            "provider": "HuggingFace",
            "model": self.model,
            "free_tier": "30,000 req/month",
            "rate_limit": "100 req/minute",
            "cost": "FREE",
            "get_key": "https://huggingface.co/settings/tokens"
        }
    
    @classmethod
    def list_available_models(cls) -> Dict[str, str]:
        """List all available free models."""
        return cls.DEFAULT_MODELS.copy()


# Convenience function for quick testing
def test_huggingface(api_key: Optional[str] = None, model: str = "llama-3.2"):
    """
    Quick test of HuggingFace adapter.
    
    Args:
        api_key: HuggingFace API key (optional if set in env)
        model: Model shorthand (llama-3.2, mistral, phi-3, qwen, flan-t5)
    """
    adapter = HuggingFaceAdapter(api_key=api_key, model=model)
    
    print(f"\n🤖 Testing HuggingFace Adapter")
    print(f"Model: {adapter.model}")
    print(f"Info: {adapter.get_model_info()}\n")
    
    # Test prompt
    prompt = "Explain what is cognitive AI in one sentence."
    context = {"signals": {"complexity": 0.8}, "concepts": {"intelligence": 0.9}}
    
    print(f"📝 Prompt: {prompt}")
    print(f"🧠 Context: {context}\n")
    
    try:
        response = adapter.infer(prompt, context)
        print(f"✅ Response: {response}\n")
        return True
    except Exception as e:
        print(f"❌ Error: {e}\n")
        return False


if __name__ == "__main__":
    # Test with environment variable
    import sys
    
    if len(sys.argv) > 1:
        model = sys.argv[1]
    else:
        model = "llama-3.2"
    
    print("Available models:", HuggingFaceAdapter.list_available_models())
    test_huggingface(model=model)

