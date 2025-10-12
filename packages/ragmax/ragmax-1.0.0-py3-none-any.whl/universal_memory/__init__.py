"""
RAGMax
Advanced RAG memory system for AI platforms via MCP
"""

__version__ = "1.0.0"
__author__ = "Vish Siddharth"

from .client import MemoryClient
from .cloud import CloudDeployment

__all__ = ["MemoryClient", "CloudDeployment"]
