"""
ASPERA - Linguaggio Cognitivo Ibrido
=====================================

Sistema di ragionamento cognitivo che combina logica simbolica e LLM
per creare agenti trasparenti, empatici e analitici.

Author: Christian Quintino De Luca - RTH Italia
Version: 0.10.5
"""

__version__ = "0.10.5"
__author__ = "Christian Quintino De Luca"
__email__ = "info@rthitalia.com"

from aspera.lang.parser import parse_aspera, validate_ast, ParseError
from aspera.runtime.engine import CognitiveEngine
from aspera.sdk.client import create_engine, run_observation

__all__ = [
    "parse_aspera",
    "validate_ast",
    "ParseError",
    "CognitiveEngine",
    "create_engine",
    "run_observation",
    "__version__",
]

