"""Configuration management for RAG CLI."""
from dataclasses import dataclass, asdict
import os
import json
from pathlib import Path


@dataclass
class Config:
    """Configuration for RAG CLI with support for environment variables."""

    # Model settings
    embedding_model: str = "text-embedding-3-small"  # OpenAI embedding model
    embedding_provider: str = "openai"  # "openai" or "ollama"
    embedding_base_url: str = "http://localhost:11434"  # Ollama base URL
    embedding_dimensions: int = 1536  # Embedding dimensions (for OpenAI models)
    llm_model: str = "gpt-4o-mini"  # Default model (OpenAI or Ollama)
    llm_provider: str = "openai"  # "openai" or "ollama" (default: openai)
    request_timeout: int = 360
    context_window: int = 32000

    # Storage (not saved to config file, always uses defaults)
    storage_dir: str = ".storage"
    documents_dir: str = "."

    # Chat settings
    chat_mode: str = "context"  # or "condense_question", "condense_plus_context"
    streaming: bool = True

    system_prompt: str = (
        "You are a helpful assistant that analyzes documents and answers questions "
        "based on the provided context. Always cite relevant information from the documents."
    )

    @classmethod
    def from_file(cls, config_path: str = ".rag_config.json"):
        """Load configuration from JSON file.

        Args:
            config_path: Path to config file (default: .rag_config.json)

        Returns:
            Config: Configuration instance with values from file
        """
        config_file = Path(config_path)

        if not config_file.exists():
            return None

        with open(config_file, 'r') as f:
            data = json.load(f)

        return cls(**data)

    def to_file(self, config_path: str = ".rag_config.json"):
        """Save configuration to JSON file.

        Args:
            config_path: Path to config file (default: .rag_config.json)
        """
        config_file = Path(config_path)

        # Exclude storage_dir and documents_dir from saved config
        config_dict = asdict(self)
        config_dict.pop('storage_dir', None)
        config_dict.pop('documents_dir', None)

        with open(config_file, 'w') as f:
            json.dump(config_dict, f, indent=2)

    @classmethod
    def from_env(cls, config_path: str = ".rag_config.json"):
        """Load configuration with priority: file > env vars > defaults.

        Priority order:
        1. .rag_config.json (if exists)
        2. Environment variables
        3. Default values

        Supported environment variables:
        - OPENAI_API_KEY: OpenAI API key (auto-enables OpenAI provider)
        - RAG_EMBEDDING_MODEL: Embedding model name
        - RAG_LLM_MODEL: LLM model name
        - RAG_LLM_PROVIDER: LLM provider (auto/openai/ollama)
        - RAG_REQUEST_TIMEOUT: Request timeout in seconds
        - RAG_CONTEXT_WINDOW: Context window size
        - RAG_CHAT_MODE: Chat mode (context/condense_question/condense_plus_context)
        - RAG_STREAMING: Enable streaming (true/false)
        - RAG_SYSTEM_PROMPT: Custom system prompt

        Args:
            config_path: Path to config file (default: .rag_config.json)

        Returns:
            Config: Configuration instance with values from file/env/defaults
        """
        # Try to load from file first
        config_from_file = cls.from_file(config_path)
        if config_from_file:
            return config_from_file

        # Auto-detect provider based on OPENAI_API_KEY
        provider = os.getenv("RAG_LLM_PROVIDER", "auto")
        if provider == "auto":
            provider = "openai" if os.getenv("OPENAI_API_KEY") else "ollama"

        # Set default model based on provider
        default_model = "gpt-4o-mini" if provider == "openai" else "granite3-dense:2b"
        llm_model = os.getenv("RAG_LLM_MODEL", default_model)

        # Set default embedding provider to match LLM provider
        default_embedding_provider = "openai" if provider == "openai" else "ollama"
        embedding_provider = os.getenv("RAG_EMBEDDING_PROVIDER", default_embedding_provider)

        # Set default embedding model based on provider
        if embedding_provider == "openai":
            default_embedding_model = "text-embedding-3-small"
        else:  # ollama
            default_embedding_model = "embeddinggemma"

        embedding_model = os.getenv("RAG_EMBEDDING_MODEL", default_embedding_model)

        config = cls(
            embedding_model=embedding_model,
            embedding_provider=embedding_provider,
            embedding_base_url=os.getenv("RAG_EMBEDDING_BASE_URL", cls.embedding_base_url),
            embedding_dimensions=int(os.getenv("RAG_EMBEDDING_DIMENSIONS", str(cls.embedding_dimensions))),
            llm_model=llm_model,
            llm_provider=provider,
            request_timeout=int(os.getenv("RAG_REQUEST_TIMEOUT", str(cls.request_timeout))),
            context_window=int(os.getenv("RAG_CONTEXT_WINDOW", str(cls.context_window))),
            storage_dir=".storage",  # Always use default
            documents_dir=".",  # Always use default
            chat_mode=os.getenv("RAG_CHAT_MODE", cls.chat_mode),
            streaming=os.getenv("RAG_STREAMING", "true").lower() == "true",
            system_prompt=os.getenv("RAG_SYSTEM_PROMPT", cls.system_prompt),
        )

        # Create default config file if it doesn't exist
        if not Path(config_path).exists():
            config.to_file(config_path)

        return config
