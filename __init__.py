"""
Zotero RAG Search System

A powerful Retrieval-Augmented Generation (RAG) system for searching 
and retrieving PDF documents from your Zotero library using semantic 
similarity and natural language queries.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"
__license__ = "MIT"

from .zotero_rag import ZoteroRAG

__all__ = ["ZoteroRAG", "__version__"]
