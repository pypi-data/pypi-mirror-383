# RAG Box

A powerful command-line tool for querying documents using RAG (Retrieval Augmented Generation). Built with LlamaIndex and supports both OpenAI and Ollama models.

## Features

- 🚀 **Dual Provider Support**: Use OpenAI (cloud) or Ollama (local) for LLM and embeddings
- 📚 **Smart Document Indexing**: Automatically indexes documents with configurable embeddings
- 💬 **Interactive & Direct Modes**: Single questions or continuous conversations
- 🔄 **Streaming Responses**: Real-time token streaming for faster perceived responses
- 💾 **Persistent Vector Store**: Reuses embeddings for instant subsequent queries
- 🎯 **Auto-Rebuild Detection**: Automatically rebuilds index when embedding config changes
- 📊 **Source Attribution**: Shows which documents contributed to each answer
- ⚙️ **Flexible Configuration**: JSON config files, environment variables, or CLI args
- 🎨 **Beautiful Output**: Formatted boxes with proper text wrapping

## Installation

### From PyPI (once published)

```bash
pip install ragbox
```

### From Source

```bash
git clone https://github.com/praysimanjuntak/ragbox.git
cd ragbox
pip install -e .
```

## Quick Start

### Using OpenAI (Recommended for Best Quality)

```bash
# Set your API key
export OPENAI_API_KEY='sk-...'

# Ask a question
ragbox "What is this project about?"
```

### Using Ollama (Local, No API Key Needed)

**Prerequisites**: Ollama server must be running with models pulled

```bash
# 1. Install and start Ollama server
# Download from https://ollama.ai
ollama serve

# 2. Pull models (required before using)
# Embedding model (choose one):
ollama pull embeddinggemma          # Recommended for embeddings

# LLM model (choose any model you prefer):
ollama pull granite4:micro          # Fast, 500MB
ollama pull llama3.2:3b            # More capable, 2GB
ollama pull qwen2.5:7b             # High quality, 4.7GB
ollama pull mistral:latest         # Or any other model you prefer

# 3. Create and configure
ragbox --init

# 4. Edit .rag_config.json to use ollama provider
# Set "llm_model" to any model you've pulled (e.g., "llama3.2:3b")
# 5. Ask questions
ragbox "What is this project about?"
```

**Note**: Replace `granite4:micro` with any Ollama model you've pulled. See available models at https://ollama.ai/library

## Usage

### Basic Commands

```bash
# Ask a single question
ragbox "What is the main purpose of this codebase?"

# Interactive mode
ragbox

# Specify documents directory
ragbox -d /path/to/docs "Summarize the key features"

# Force rebuild index
ragbox --rebuild

# List indexed files
ragbox --list-files

# Verbose output (show timing and config)
ragbox --verbose "question"

# Plain text output (easy to copy)
ragbox --format copy "question"
```

### Command-Line Options

```
usage: ragbox [-h] [-d DOCS_DIR] [-s STORAGE_DIR] [-m MODEL] [--rebuild]
              [--list-files] [-v] [--format {box,copy}] [--init] [question]

positional arguments:
  question              Question to ask (if not provided, enters interactive mode)

options:
  -h, --help            show this help message and exit
  -d DOCS_DIR, --docs-dir DOCS_DIR
                        Directory containing documents (default: current directory)
  -s STORAGE_DIR, --storage-dir STORAGE_DIR
                        Directory for storing index (default: .storage)
  -m MODEL, --model MODEL
                        LLM model to use
  --rebuild             Force rebuild of index
  --list-files          List indexed files and exit
  -v, --verbose         Show detailed initialization logs
  --format {box,copy}   Output format: 'box' (default) or 'copy' (plain text)
  --init                Create a default .rag_config.json file
```

## Configuration

### Configuration File

Create a `.rag_config.json` file in your project directory:

```bash
ragbox --init
```

Example configuration:

```json
{
  "embedding_model": "text-embedding-3-small",
  "embedding_provider": "openai",
  "embedding_base_url": "http://localhost:11434",
  "embedding_dimensions": 1536,
  "llm_model": "gpt-4o-mini",
  "llm_provider": "openai",
  "request_timeout": 360,
  "context_window": 32000,
  "chat_mode": "context",
  "streaming": true,
  "system_prompt": "You are a helpful assistant that analyzes documents and answers questions based on the provided context. Always cite relevant information from the documents."
}
```

### Provider Options

**OpenAI (Recommended)**
```json
{
  "embedding_provider": "openai",
  "embedding_model": "text-embedding-3-small",
  "llm_provider": "openai",
  "llm_model": "gpt-4o-mini"
}
```

**Ollama (Local)**
```json
{
  "embedding_provider": "ollama",
  "embedding_model": "embeddinggemma",
  "llm_provider": "ollama",
  "llm_model": "granite4:micro"
}
```

**Note**: You can use any Ollama model for `llm_model` - just replace `granite4:micro` with any model you've pulled (e.g., `llama3.2:3b`, `mistral:latest`, `qwen2.5:7b`, etc.). See all available models at https://ollama.ai/library

**Mix and Match Providers**

You can use different providers for embeddings and LLM:

```json
{
  "embedding_provider": "ollama",
  "embedding_model": "embeddinggemma",
  "llm_provider": "openai",
  "llm_model": "gpt-4o-mini"
}
```

### Switching Between Providers

To switch from Ollama to OpenAI (or vice versa):

1. **Edit `.rag_config.json`** and update the provider settings:
   ```json
   {
     "embedding_provider": "openai",
     "embedding_model": "text-embedding-3-small",
     "llm_provider": "openai",
     "llm_model": "gpt-4o-mini"
   }
   ```

2. **Set your API key** (for OpenAI):
   ```bash
   export OPENAI_API_KEY='sk-...'
   ```

3. **Rebuild the index** (required when changing embedding provider):
   ```bash
   ragbox --rebuild
   ```

**Note**: When you change the embedding provider or model, the index will automatically rebuild on the next run.

### Environment Variables

```bash
# Required for OpenAI
export OPENAI_API_KEY='sk-...'

# Optional overrides
export RAG_EMBEDDING_MODEL="text-embedding-3-small"
export RAG_EMBEDDING_PROVIDER="openai"
export RAG_LLM_MODEL="gpt-4o-mini"
export RAG_LLM_PROVIDER="openai"
export RAG_CHAT_MODE="context"
export RAG_STREAMING="true"
```

## How It Works

1. **First Run**: Loads documents → Creates embeddings → Saves vector index
2. **Subsequent Runs**: Loads existing index (instant startup)
3. **Config Change Detection**: Automatically rebuilds if embedding config changes
4. **Query Processing**:
   - Embeds your question
   - Retrieves relevant document chunks
   - Sends context + question to LLM
   - Streams back the answer with sources

## Supported File Types

- **Text files**: `.txt`, `.md`, `.rst`
- **Code files**: `.py`, `.js`, `.java`, `.cpp`, `.go`, `.ts`, `.html`, `.css`, `.sh`, etc.
- **Documents**: `.pdf`, `.docx`, `.epub`, `.ppt`, `.pptx`, `.pptm`
- **Data files**: `.csv`, `.json`, `.yaml`, `.xml`
- **Notebooks**: `.ipynb` (Jupyter Notebooks)
- **Images**: `.png`, `.jpg`, `.jpeg` (with OCR/vision capabilities)
- **Media**: `.mp3`, `.mp4` (audio/video transcription)
- **Email**: `.mbox` (email archives)
- **Other**: `.hwp` (Hangul Word Processor)

All files are processed via LlamaIndex's SimpleDirectoryReader, which automatically detects file types and uses appropriate parsers.

### Auto-Excluded

- `.storage`, `.git`, `.venv`, `venv`, `node_modules`
- `__pycache__`, `.pytest_cache`, `.mypy_cache`
- `*.log`, `*.pyc`

## Examples

### Analyze a Codebase

```bash
cd my-project
ragbox "Explain the authentication flow"
ragbox "Are there any security issues?"
ragbox "How is the database configured?"
```

### Query CCTV/Security Logs

Perfect for analyzing large log files quickly:

```bash
# Point to your logs directory
cd /var/log/security
ragbox "Show me all failed login attempts from yesterday"
ragbox "Were there any suspicious access patterns?"
ragbox "Summarize the security events from IP 192.168.1.100"

# Or specify the directory
ragbox -d /var/log/cctv "When did motion detection trigger last night?"
ragbox -d /var/log/cctv "List all events between 10pm and 6am"
```

**How it works**: RAG CLI indexes all log files, allowing you to ask natural language questions instead of manually searching through thousands of lines. The AI retrieves relevant log entries and provides contextual answers.

### Research Papers

```bash
ragbox -d ~/papers "Compare the methodologies"
ragbox -d ~/papers "What are the main findings?"
```

### Documentation

```bash
ragbox -d ./docs "How do I setup the project?"
ragbox -d ./docs --rebuild  # After updating docs
```

### Interactive Session

```bash
$ ragbox

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💬 RAG Box - Interactive Mode
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📁 Documents: /home/user/docs
📚 Indexed files: 42
🤖 Model: gpt-4o-mini

Commands:
  /exit, /quit - Exit the program
  /files - List indexed files
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❯ What are the main topics covered?
[Answer with sources...]

❯ Tell me more about topic X
[Continued conversation with context...]

❯ /exit
👋 Goodbye!
```

## Troubleshooting

### OpenAI API Key Issues

```bash
# Verify key is set
echo $OPENAI_API_KEY

# Set the key
export OPENAI_API_KEY='sk-...'
```

### Ollama Connection Issues

**Important**: Make sure Ollama server is running and required models are pulled!

```bash
# Start Ollama server (required!)
ollama serve

# Check what's running
ollama ps

# Pull required models if not already pulled
ollama pull embeddinggemma    # For embeddings
ollama pull granite4:micro    # For LLM (or any other model)

# Verify models are available
ollama list

# Keep models loaded in memory for faster response
ollama run granite4:micro
# Press Ctrl+D to exit but keep loaded
```

Common issues:
- **"Connection refused"**: Ollama server not running → Run `ollama serve`
- **"Model not found"**: Models not pulled → Run `ollama pull <model-name>`
- **Slow responses**: Models loading from disk → Keep them loaded with `ollama run <model>`

### Index/Embedding Mismatch

Don't worry! The tool automatically detects config changes and rebuilds:

```bash
# Or force rebuild manually
ragbox --rebuild
```

### No Documents Found

```bash
# Check current directory
ls -la

# Specify directory explicitly
ragbox -d /path/to/docs "question"
```

## Performance Tips

1. **OpenAI**: Faster embeddings, better quality, requires API key
2. **Ollama**: Free, local, but slower (keep models loaded: `ollama run model`)
3. **Index Reuse**: First run is slow (embedding creation), subsequent runs are instant
4. **Streaming**: Enabled by default for faster perceived response
5. **Model Choice**: Smaller models (granite4:micro) faster, larger models (gpt-4o) better quality

## Development

```bash
git clone https://github.com/praysimanjuntak/ragbox.git
cd ragbox
pip install -e ".[dev]"
```

## Roadmap

- [x] OpenAI and Ollama support
- [x] Streaming responses
- [x] Auto-rebuild on config change
- [x] Source attribution
- [x] Interactive mode
- [x] Configurable output format
- [ ] **Image document support with OCR** (planned for next update)
- [ ] Web search integration
- [ ] Conversation history export
- [ ] Query caching

## License

MIT License

## Acknowledgments

- [LlamaIndex](https://www.llamaindex.ai/) - RAG framework
- [OpenAI](https://openai.com/) - Cloud embeddings and LLMs
- [Ollama](https://ollama.ai/) - Local LLM runtime

---

**Author**: Pray Apostel Simanjuntak

If you find this project helpful, please consider giving it a ⭐ on [GitHub](https://github.com/praysimanjuntak/ragbox)!
