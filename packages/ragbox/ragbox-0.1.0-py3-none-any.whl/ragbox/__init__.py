"""RAG CLI - Command-line tool for asking questions about your documents using RAG."""

__version__ = "0.1.0"

# Lazy imports to speed up CLI startup
__all__ = ["Config", "RAGEngine"]

def __getattr__(name):
    """Lazy load modules to speed up initial import."""
    if name == "Config":
        from .config import Config
        return Config
    elif name == "RAGEngine":
        from .rag_engine import RAGEngine
        return RAGEngine
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
