"""
ASPERA LLM Adapters
===================
Adapters per integrare diversi LLM providers.

Author: Christian Quintino De Luca - RTH Italia
"""

from aspera.runtime.llm_adapters.groq_adapter import GroqAdapter
from aspera.runtime.llm_adapters.huggingface_adapter import HuggingFaceAdapter

__all__ = ["GroqAdapter", "HuggingFaceAdapter"]

