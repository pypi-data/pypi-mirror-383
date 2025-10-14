"""
LangSwift: Drop-in OpenAI replacement for SLM optimization
"""

__version__ = "0.1.0"

# Re-export the main class for convenience
from .openai import OpenAI

__all__ = ["OpenAI"]
