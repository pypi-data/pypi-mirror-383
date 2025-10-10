"""
RAG URL Agent - Simple Python library for URL processing with RAG
"""

__version__ = "1.0.0"
__author__ = "Your Name"

# Core imports
from .simple_api import SimpleAgent, quick_agent

# Full agent (for advanced usage)
from .agent import RAGAgent

# Version info
__all__ = [
    "SimpleAgent",
    "quick_agent",
    "RAGAgent",
    "__version__",
]