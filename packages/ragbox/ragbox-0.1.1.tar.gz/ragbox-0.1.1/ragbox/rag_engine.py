"""Core RAG engine implementation using LlamaIndex."""
import os
import sys
import json
from typing import List, Optional
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO

from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    Settings,
    StorageContext,
    load_index_from_storage,
)
from llama_index.core.memory import ChatMemoryBuffer

from .config import Config


class RAGEngine:
    """RAG engine for document indexing and question answering."""

    def __init__(self, config: Config, verbose: bool = False):
        """Initialize RAG engine with configuration.

        Args:
            config: Configuration object
            verbose: Show detailed logging
        """
        self.config = config
        self.verbose = verbose
        self.index: Optional[VectorStoreIndex] = None
        self.chat_engine = None
        self.indexed_files: List[str] = []
        self.created_new_index: bool = False  # Track if new index was created

    def initialize(self):
        """Initialize the RAG engine by setting up models, index, and chat engine."""
        if self.verbose:
            print("Setting up models...")
        self._setup_models()
        if self.verbose:
            print("Setting up index...")
        self._setup_index()
        if self.verbose:
            print("Setting up chat engine...")
        self._setup_chat_engine()
        if self.verbose:
            print("Initialization complete!")

    def _check_ollama_model_available(self, model_name: str) -> bool:
        """Check if an Ollama model is available.

        Args:
            model_name: Name of the model to check

        Returns:
            True if model is available, False otherwise
        """
        try:
            import ollama
            client = ollama.Client(host=self.config.embedding_base_url)
            response = client.list()
            # Check if model is in the list
            # response.models is a list of Model objects with .model attribute
            for model in response.models:
                if model.model.startswith(model_name):
                    return True
            return False
        except Exception:
            # Ollama library not available or error occurred
            return False

    def _setup_models(self):
        """Configure embedding and LLM models in global Settings."""
        # Set up embedding model based on provider (lazy import)
        if self.config.embedding_provider == "openai":
            # Use OpenAI embeddings - fastest startup!
            from llama_index.embeddings.openai import OpenAIEmbedding

            if self.verbose:
                print(f"Using OpenAI embeddings: {self.config.embedding_model}")
            Settings.embed_model = OpenAIEmbedding(
                model=self.config.embedding_model,
                dimensions=self.config.embedding_dimensions,
                # api_key is read from OPENAI_API_KEY env var by default
            )
        elif self.config.embedding_provider == "ollama":
            # Check if embedding model is available
            if not self._check_ollama_model_available(self.config.embedding_model):
                raise ValueError(
                    f"Ollama embedding model '{self.config.embedding_model}' not found.\n"
                    f"Please pull it first: ollama pull {self.config.embedding_model}\n"
                    f"Or check available models: ollama list"
                )

            # Use Ollama embeddings - fast startup, no torch/transformers!
            from llama_index.embeddings.ollama import OllamaEmbedding

            if self.verbose:
                print(f"Using Ollama embeddings: {self.config.embedding_model}")
            Settings.embed_model = OllamaEmbedding(
                model_name=self.config.embedding_model,
                base_url=self.config.embedding_base_url,
            )
        else:
            raise ValueError(f"Unsupported embedding provider: {self.config.embedding_provider}. Use 'openai' or 'ollama'.")

        # Set up LLM based on provider (lazy import to avoid unnecessary dependencies)
        if self.config.llm_provider == "openai":
            # Use OpenAI - only import when needed
            from llama_index.llms.openai import OpenAI

            Settings.llm = OpenAI(
                model=self.config.llm_model,
                timeout=float(self.config.request_timeout),
                temperature=0.7,  # Reasonable default for Q&A
                max_retries=3,
                # api_key is read from OPENAI_API_KEY env var by default
            )
        else:
            # Check if LLM model is available
            if not self._check_ollama_model_available(self.config.llm_model):
                raise ValueError(
                    f"Ollama LLM model '{self.config.llm_model}' not found.\n"
                    f"Please pull it first: ollama pull {self.config.llm_model}\n"
                    f"Or check available models: ollama list"
                )

            # Use Ollama - only import when needed
            from llama_index.llms.ollama import Ollama

            Settings.llm = Ollama(
                model=self.config.llm_model,
                request_timeout=self.config.request_timeout,
                context_window=self.config.context_window,
                keep_alive=-1,  # Keep model loaded in memory
            )

    def _check_embedding_config_match(self) -> bool:
        """Check if current embedding config matches the saved one.

        Returns:
            True if config matches, False otherwise
        """
        embedding_config_path = os.path.join(self.config.storage_dir, "embedding_config.json")

        if not os.path.exists(embedding_config_path):
            # Old index without config file - assume mismatch
            return False

        with open(embedding_config_path, "r") as f:
            saved_config = json.load(f)

        # Check if provider or model changed
        if (saved_config.get("embedding_provider") != self.config.embedding_provider or
            saved_config.get("embedding_model") != self.config.embedding_model):
            if self.verbose:
                print(f"Config mismatch - was: {saved_config.get('embedding_provider')}/{saved_config.get('embedding_model')}, "
                      f"now: {self.config.embedding_provider}/{self.config.embedding_model}")
            return False

        return True

    def _setup_index(self):
        """Load existing vector index or create a new one."""
        index_file = os.path.join(self.config.storage_dir, "docstore.json")

        if os.path.exists(index_file):
            if self.verbose:
                print(f"Loading existing index from {self.config.storage_dir}...")

            # Check if embedding configuration matches
            if not self._check_embedding_config_match():
                print(f"⚠ Embedding configuration changed. Rebuilding index...")
                self._create_new_index()
            else:
                self._load_existing_index()
        else:
            if self.verbose:
                print(f"Creating new index from documents in {self.config.documents_dir}...")
            self._create_new_index()

    def _create_new_index(self):
        """Create new vector index from documents."""
        self.created_new_index = True  # Mark that we're creating a new index
        os.makedirs(self.config.storage_dir, exist_ok=True)

        # Exclude storage, logs, and common directories
        exclude_files = [
            self.config.storage_dir,
            "*.log",
            "__pycache__",
            ".git",
            ".venv",
            "venv",
            "node_modules",
            ".pytest_cache",
            ".mypy_cache",
            "*.pyc",
        ]

        # Print newline to clear the spinner, then show indexing progress
        if not self.verbose:
            print()  # Clear the "Initializing..." line
        # Load documents recursively - always show this message on first index
        # Show absolute path if documents_dir is "." for clarity
        docs_path = os.path.abspath(self.config.documents_dir)
        print(f"Loading documents from {docs_path}...")
        documents = SimpleDirectoryReader(
            self.config.documents_dir,
            filename_as_id=True,
            exclude=exclude_files,
            recursive=True,
        ).load_data()

        if not documents:
            raise ValueError(f"No documents found in {self.config.documents_dir}")

        # Always show progress on first-time indexing
        print(f"Found {len(documents)} documents. Creating embeddings...")

        # Track indexed files
        self.indexed_files = [
            doc.metadata.get("file_name", "Unknown") for doc in documents
        ]

        # Create vector index - always show progress on first index
        self.index = VectorStoreIndex.from_documents(
            documents=documents,
            embed_model=Settings.embed_model,
            show_progress=True,
        )

        # Persist to disk
        print(f"Persisting index to {self.config.storage_dir}...")
        self.index.storage_context.persist(self.config.storage_dir)

        # Save file list
        file_list_path = os.path.join(self.config.storage_dir, "indexed_files.json")
        with open(file_list_path, "w") as f:
            json.dump(self.indexed_files, f, indent=2)

        # Save embedding configuration
        embedding_config_path = os.path.join(self.config.storage_dir, "embedding_config.json")
        embedding_config = {
            "embedding_provider": self.config.embedding_provider,
            "embedding_model": self.config.embedding_model,
            "embedding_dimensions": self.config.embedding_dimensions,
        }
        with open(embedding_config_path, "w") as f:
            json.dump(embedding_config, f, indent=2)

        print(f"Indexed {len(self.indexed_files)} files")

    def _load_existing_index(self):
        """Load existing vector index from storage."""
        # Suppress verbose LlamaIndex loading messages unless verbose mode
        if not self.verbose:
            # Redirect stdout and stderr to suppress loading messages
            f = StringIO()
            with redirect_stdout(f), redirect_stderr(f):
                storage_context = StorageContext.from_defaults(
                    persist_dir=self.config.storage_dir
                )
                self.index = load_index_from_storage(
                    storage_context=storage_context,
                    embed_model=Settings.embed_model,
                )
        else:
            storage_context = StorageContext.from_defaults(
                persist_dir=self.config.storage_dir
            )
            self.index = load_index_from_storage(
                storage_context=storage_context,
                embed_model=Settings.embed_model,
            )

        # Load file list
        file_list_path = os.path.join(self.config.storage_dir, "indexed_files.json")
        if os.path.exists(file_list_path):
            with open(file_list_path, "r") as f:
                self.indexed_files = json.load(f)
            if self.verbose:
                print(f"Loaded index with {len(self.indexed_files)} files")

    def _setup_chat_engine(self):
        """Initialize chat engine with memory."""
        if not self.index:
            raise RuntimeError("Index must be created before setting up chat engine")

        # Get context window from config or LLM
        context_window = self.config.context_window
        if hasattr(Settings.llm, 'context_window'):
            context_window = Settings.llm.context_window

        memory = ChatMemoryBuffer.from_defaults(
            token_limit=context_window
        )

        self.chat_engine = self.index.as_chat_engine(
            chat_mode=self.config.chat_mode,
            llm=Settings.llm,
            streaming=self.config.streaming,
            memory=memory,
            system_prompt=self.config.system_prompt,
        )

    def chat(self, question: str):
        """Send a chat message and get response (non-streaming).

        Args:
            question: User question

        Returns:
            Response object with answer

        Raises:
            RuntimeError: If chat engine not initialized
        """
        if not self.chat_engine:
            raise RuntimeError("Chat engine not initialized")
        return self.chat_engine.chat(question)

    def stream_chat(self, question: str):
        """Send a chat message and stream response.

        Args:
            question: User question

        Returns:
            Streaming response object

        Raises:
            RuntimeError: If chat engine not initialized
        """
        if not self.chat_engine:
            raise RuntimeError("Chat engine not initialized")
        return self.chat_engine.stream_chat(question)

    def get_indexed_files(self) -> List[str]:
        """Get list of indexed files.

        Returns:
            List of indexed file paths
        """
        return self.indexed_files.copy()
