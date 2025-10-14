#!/usr/bin/env python3
"""Command-line interface for RAG CLI."""
import argparse
import re
import sys
import warnings
from pathlib import Path

# Suppress pydantic warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")


# ANSI color codes
class Colors:
    """ANSI color codes for terminal output."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Colors
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    GRAY = "\033[90m"
    WHITE = "\033[97m"


def clean_token(token: str) -> str:
    """Clean a single token by removing citation markers.

    Args:
        token: Token to clean

    Returns:
        Cleaned token
    """
    # Remove inline citation markers like ^[
    token = token.replace('^[', '')
    return token


def wrap_text(text: str, width: int = 75, indent: str = "  ") -> str:
    """Wrap text to a specific width with indentation.

    Args:
        text: Text to wrap
        width: Maximum width (default 75)
        indent: Indentation for each line (default "  ")

    Returns:
        Wrapped text
    """
    import textwrap

    # Split into paragraphs
    paragraphs = text.split('\n\n')
    wrapped_paragraphs = []

    for para in paragraphs:
        if para.strip():
            # Wrap each paragraph
            wrapped = textwrap.fill(para.strip(), width=width,
                                   initial_indent=indent,
                                   subsequent_indent=indent)
            wrapped_paragraphs.append(wrapped)

    return '\n│\n'.join(wrapped_paragraphs)


def strip_ansi(text: str) -> str:
    """Remove ANSI color codes from text.

    Args:
        text: Text with ANSI codes

    Returns:
        Text without ANSI codes
    """
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


def print_box(title: str, content: str, color: str = Colors.BLUE, format_type: str = "box"):
    """Print content in a box with title or plain format.

    Args:
        title: Title for the box
        content: Content to display
        color: Color for the box (default blue)
        format_type: "box" for bordered box, "copy" for plain text
    """
    if format_type == "copy":
        # Plain format for easy copying
        print(f"{Colors.BOLD}{color}{title}:{Colors.RESET}")
        print()
        print(content)
        print()
    else:
        # Box format
        width = 100  # Increased width for better readability

        # Top border with title
        # ╭─ title ───╮ should align with │...│ below
        # Need: initial ─, space, title, space, dashes to fill to width
        print(f"{color}╭─ {Colors.BOLD}{title}{Colors.RESET}{color} {'─' * (width - len(title) - 3)}╮{Colors.RESET}")
        print(f"{color}│{Colors.RESET}{' ' * width}{color}│{Colors.RESET}")

        # Content lines
        for line in content.split('\n'):
            # Pad line to width (accounting for ANSI codes)
            visible_len = len(strip_ansi(line))
            padding = width - visible_len
            print(f"{color}│{Colors.RESET}{line}{' ' * padding}{color}│{Colors.RESET}")

        print(f"{color}│{Colors.RESET}{' ' * width}{color}│{Colors.RESET}")
        # Bottom border
        print(f"{color}╰{'─' * width}╯{Colors.RESET}")
        print()


def format_response_text(text: str) -> str:
    """Format response text for better readability.

    Args:
        text: Raw response text

    Returns:
        Formatted text with proper line breaks
    """
    # Remove inline citation markers like ^[
    text = re.sub(r'\^\[', '', text)

    # Remove inline citations in parentheses like (Classification and Species Diversity)
    # Match parentheses with capitalized words that look like section titles
    text = re.sub(r'\s*\([A-Z][^)]*\)\s*', ' ', text)

    # Remove reference markers like (Ref: #1), [1], etc.
    text = re.sub(r'\s*\(Ref:\s*#?\d+\)\s*', ' ', text)
    text = re.sub(r'\s*\[\d+\]\s*', ' ', text)

    # Remove "(source)" and similar generic markers
    text = re.sub(r'\s*\(source\)\s*', '', text, flags=re.IGNORECASE)

    # Clean up extra spaces
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()

    # Add line breaks after sentences for better readability
    # Look for '. ' followed by a capital letter and add extra newline
    formatted = re.sub(r'\. ([A-Z])', r'.\n\n\1', text)

    return formatted


def parse_arguments():
    """Parse command-line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="RAG CLI - Ask questions about your documents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Ask a single question
  ragbox "What is this project about?"

  # Interactive mode
  ragbox

  # Specify documents directory
  ragbox -d /path/to/docs "Summarize the main features"

  # Use different model
  ragbox -m llama3.2:3b "What are the key findings?"

  # Force rebuild index
  ragbox --rebuild "Tell me about the changes"
        """,
    )
    parser.add_argument(
        "question",
        nargs="?",
        help="Question to ask (if not provided, enters interactive mode)",
    )
    parser.add_argument(
        "-d",
        "--docs-dir",
        type=str,
        default=".",
        help="Directory containing documents (default: current directory)",
    )
    parser.add_argument(
        "-s",
        "--storage-dir",
        type=str,
        default=".storage",
        help="Directory for storing index (default: .storage)",
    )
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        help="LLM model to use (default: granite3-dense:2b)",
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Force rebuild of index",
    )
    parser.add_argument(
        "--list-files",
        action="store_true",
        help="List indexed files and exit",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed initialization logs",
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["box", "copy"],
        default="box",
        help="Output format: 'box' (default, with borders) or 'copy' (plain text, easy to copy)",
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="Create a default .rag_config.json file in the current directory",
    )
    return parser.parse_args()


def main():
    """Main entry point for RAG CLI."""
    args = parse_arguments()

    # Handle --init command
    if args.init:
        from .config import Config
        import os

        config_path = Path(".rag_config.json")
        if config_path.exists():
            print(f"{Colors.YELLOW}⚠ .rag_config.json already exists!{Colors.RESET}")
            response = input("Overwrite? (y/N): ")
            if response.lower() != 'y':
                print("Cancelled.")
                sys.exit(0)

        # Auto-detect provider based on OPENAI_API_KEY
        if os.getenv("OPENAI_API_KEY"):
            # OpenAI defaults
            config = Config()
        else:
            # Ollama defaults
            config = Config(
                embedding_model="embeddinggemma",
                embedding_provider="ollama",
                llm_model="granite3-dense:2b",
                llm_provider="ollama"
            )
        config.to_file(".rag_config.json")

        print(f"{Colors.GREEN}✓ Created .rag_config.json{Colors.RESET}")
        print(f"\n{Colors.CYAN}Configuration file created with default settings:{Colors.RESET}")
        print(f"  • LLM Provider: {Colors.BOLD}{config.llm_provider}{Colors.RESET}")
        print(f"  • LLM Model: {Colors.BOLD}{config.llm_model}{Colors.RESET}")
        print(f"  • Embedding Model: {Colors.BOLD}{config.embedding_model}{Colors.RESET}")
        print(f"  • Context Window: {Colors.BOLD}{config.context_window}{Colors.RESET}")
        print(f"  • Streaming: {Colors.BOLD}{config.streaming}{Colors.RESET}")
        print(f"\n{Colors.GRAY}Edit .rag_config.json to customize your settings.{Colors.RESET}")
        sys.exit(0)

    # Print initialization message BEFORE heavy imports
    if not args.verbose and not args.list_files:
        print(f"{Colors.CYAN}⚡ Initializing RAG engine...{Colors.RESET}", end="", flush=True)

    # Import after printing message for perceived faster startup
    from .config import Config
    from .rag_engine import RAGEngine

    # Create config from environment
    config = Config.from_env()

    # Override with command-line arguments
    if args.docs_dir:
        config.documents_dir = args.docs_dir
    if args.storage_dir:
        config.storage_dir = args.storage_dir
    if args.model:
        config.llm_model = args.model

    # Validate OpenAI API key if provider is OpenAI
    import os
    if config.llm_provider == "openai" and not os.getenv("OPENAI_API_KEY"):
        print(f"\n{Colors.YELLOW}✗ Error:{Colors.RESET} OpenAI provider selected but OPENAI_API_KEY not found!", file=sys.stderr)
        print(f"\n{Colors.CYAN}Solutions:{Colors.RESET}")
        print(f"  1. Set your API key: {Colors.GREEN}export OPENAI_API_KEY='sk-...'{Colors.RESET}")
        print(f"  2. Or switch to Ollama in .rag_config.json:")
        print(f'     {Colors.GREEN}{{"llm_provider": "ollama", "llm_model": "granite3-dense:2b"}}{Colors.RESET}')
        sys.exit(1)

    # Handle rebuild
    if args.rebuild and Path(config.storage_dir).exists():
        import shutil

        print(f"\nRemoving existing index at {config.storage_dir}...")
        shutil.rmtree(config.storage_dir)
        if not args.verbose:
            print(f"{Colors.CYAN}⚡ Initializing RAG engine...{Colors.RESET}", end="", flush=True)

    # Initialize engine
    try:
        engine = RAGEngine(config, verbose=args.verbose)
        engine.initialize()
        # Only print checkmark if we didn't create a new index (which has its own output)
        if not args.verbose and not engine.created_new_index:
            print(f" {Colors.GREEN}✓{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.YELLOW}✗ Error:{Colors.RESET} {e}", file=sys.stderr)
        sys.exit(1)

    # Handle list files
    if args.list_files:
        files = engine.get_indexed_files()
        print(f"\nIndexed {len(files)} files:")
        for file in sorted(files):
            print(f"  - {file}")
        sys.exit(0)

    # Direct question mode
    if args.question:
        try:
            print()  # Blank line

            if args.verbose:
                import time
                print(f"{Colors.DIM}Embedding query with {config.embedding_provider}/{config.embedding_model}...{Colors.RESET}")
                query_start = time.time()

            if config.streaming:
                # Use streaming with real-time display
                response = engine.stream_chat(args.question)

                if args.verbose:
                    query_time = time.time() - query_start
                    print(f"{Colors.DIM}Query embedded and context retrieved in {query_time:.2f}s{Colors.RESET}")

                if args.format == "copy":
                    # Simple streaming for copy format
                    print(f"{Colors.BOLD}{Colors.CYAN}Answer:{Colors.RESET}")
                    print()
                    full_response = ""
                    for token in response.response_gen:
                        full_response += token
                        cleaned = clean_token(token)
                        print(cleaned, end="", flush=True)
                    print("\n")
                else:
                    # Box format with streaming
                    width = 100
                    print(f"{Colors.CYAN}╭─ {Colors.BOLD}Answer{Colors.RESET}{Colors.CYAN} {'─' * (width - 9)}╮{Colors.RESET}")
                    print(f"{Colors.CYAN}│{Colors.RESET}{' ' * width}{Colors.CYAN}│{Colors.RESET}")
                    print(f"{Colors.CYAN}│{Colors.RESET}  {Colors.DIM}Thinking...{Colors.RESET}", end="", flush=True)

                    # Stream tokens in real-time
                    full_response = ""
                    col = 2  # Starting column position
                    first_token = True
                    for token in response.response_gen:
                        # Clear "Thinking..." on first token
                        if first_token:
                            print(f"\r{Colors.CYAN}│{Colors.RESET}  ", end="", flush=True)
                            first_token = False
                        full_response += token
                        cleaned = clean_token(token)

                        # Simple word wrapping during streaming
                        for char in cleaned:
                            if char == '\n' or col >= width - 2:
                                # New line
                                padding = width - col
                                print(f"{' ' * padding}{Colors.CYAN}│{Colors.RESET}")
                                print(f"{Colors.CYAN}│{Colors.RESET}  ", end="", flush=True)
                                col = 2
                                if char != '\n':
                                    print(char, end="", flush=True)
                                    col += 1
                            else:
                                print(char, end="", flush=True)
                                col += 1

                    # Close the line and box
                    padding = width - col
                    print(f"{' ' * padding}{Colors.CYAN}│{Colors.RESET}")
                    print(f"{Colors.CYAN}│{Colors.RESET}{' ' * width}{Colors.CYAN}│{Colors.RESET}")
                    print(f"{Colors.CYAN}╰{'─' * width}╯{Colors.RESET}")
                    print()

                # Format sources
                if hasattr(response, 'source_nodes') and response.source_nodes:
                    source_lines = []
                    seen_files = set()
                    for node in response.source_nodes:
                        filename = node.metadata.get('file_name', 'Unknown')
                        if filename not in seen_files:
                            seen_files.add(filename)
                            # Get relevance score if available
                            score = node.score if hasattr(node, 'score') and node.score else 0
                            score_pct = int(score * 100) if score else 0
                            if args.format == "copy":
                                source_lines.append(f"• {filename} (Relevance: {score_pct}%)")
                            else:
                                # Format: "  • filename (Relevance: XX%)"
                                # Max width inside box is 96 chars (100 - 2 padding on each side)
                                # "  • " = 4, " (Relevance: " = 13, "XX%)" = 4-5 chars
                                # So filename space = 96 - 4 - 13 - 5 = 74 chars
                                source_lines.append(f"  • {filename:<74}(Relevance: {score_pct}%)")

                    sources_content = '\n'.join(source_lines)
                    print_box("Sources", sources_content, Colors.BLUE, args.format)
            else:
                # Non-streaming
                response = engine.chat(args.question)
                formatted_response = format_response_text(response.response)

                if args.format == "copy":
                    # Plain format
                    print(f"{Colors.BOLD}{Colors.CYAN}Answer:{Colors.RESET}")
                    print()
                    print(formatted_response)
                    print()
                else:
                    # Wrap text for box display
                    wrapped_content = wrap_text(formatted_response)

                    # Print answer in box
                    print_box("Answer", wrapped_content, Colors.CYAN, args.format)

                # Format sources
                if hasattr(response, 'source_nodes') and response.source_nodes:
                    source_lines = []
                    seen_files = set()
                    for node in response.source_nodes:
                        filename = node.metadata.get('file_name', 'Unknown')
                        if filename not in seen_files:
                            seen_files.add(filename)
                            # Get relevance score if available
                            score = node.score if hasattr(node, 'score') and node.score else 0
                            score_pct = int(score * 100) if score else 0
                            if args.format == "copy":
                                source_lines.append(f"• {filename} (Relevance: {score_pct}%)")
                            else:
                                # Format: "  • filename (Relevance: XX%)"
                                # Max width inside box is 96 chars (100 - 2 padding on each side)
                                # "  • " = 4, " (Relevance: " = 13, "XX%)" = 4-5 chars
                                # So filename space = 96 - 4 - 13 - 5 = 74 chars
                                source_lines.append(f"  • {filename:<74}(Relevance: {score_pct}%)")

                    sources_content = '\n'.join(source_lines)
                    print_box("Sources", sources_content, Colors.BLUE, args.format)

            sys.exit(0)
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}⚠ Interrupted{Colors.RESET}", file=sys.stderr)
            sys.exit(130)
        except Exception as e:
            print(f"{Colors.YELLOW}✗ Error:{Colors.RESET} {e}", file=sys.stderr)
            sys.exit(1)

    # Interactive mode
    print(f"\n{Colors.CYAN}{'━' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}💬 RAG CLI - Interactive Mode{Colors.RESET}")
    print(f"{Colors.CYAN}{'━' * 60}{Colors.RESET}")
    print(f"{Colors.BLUE}📁 Documents:{Colors.RESET} {config.documents_dir}")
    print(f"{Colors.BLUE}📚 Indexed files:{Colors.RESET} {len(engine.get_indexed_files())}")
    print(f"{Colors.BLUE}🤖 Model:{Colors.RESET} {config.llm_model}")
    print(f"\n{Colors.YELLOW}Commands:{Colors.RESET}")
    print(f"  {Colors.GREEN}/exit, /quit{Colors.RESET} - Exit the program")
    print(f"  {Colors.GREEN}/files{Colors.RESET} - List indexed files")
    print(f"  {Colors.GREEN}/clear{Colors.RESET} - Clear chat history (not yet implemented)")
    print(f"{Colors.CYAN}{'━' * 60}{Colors.RESET}\n")

    while True:
        try:
            question = input(f"\n{Colors.MAGENTA}❯{Colors.RESET} ")

            if not question.strip():
                continue

            # Handle commands
            if question.strip() in ["/exit", "/quit"]:
                print(f"{Colors.GREEN}👋 Goodbye!{Colors.RESET}")
                break

            if question.strip() == "/files":
                files = engine.get_indexed_files()
                print(f"\n{Colors.BLUE}📚 Indexed {len(files)} files:{Colors.RESET}")
                for file in sorted(files):
                    print(f"  {Colors.GRAY}•{Colors.RESET} {file}")
                continue

            # Process question
            print()  # Blank line
            if config.streaming:
                response = engine.stream_chat(question)

                # Print opening box
                width = 100
                print(f"{Colors.CYAN}╭─ {Colors.BOLD}Answer{Colors.RESET}{Colors.CYAN} {'─' * (width - 9)}╮{Colors.RESET}")
                print(f"{Colors.CYAN}│{Colors.RESET}{' ' * width}{Colors.CYAN}│{Colors.RESET}")
                print(f"{Colors.CYAN}│{Colors.RESET}  {Colors.DIM}Thinking...{Colors.RESET}", end="", flush=True)

                # Stream tokens in real-time
                full_response = ""
                col = 2  # Starting column position
                first_token = True
                for token in response.response_gen:
                    # Clear "Thinking..." on first token
                    if first_token:
                        print(f"\r{Colors.CYAN}│{Colors.RESET}  ", end="", flush=True)
                        first_token = False
                    full_response += token
                    cleaned = clean_token(token)

                    # Simple word wrapping during streaming
                    for char in cleaned:
                        if char == '\n' or col >= width - 2:
                            # New line
                            padding = width - col
                            print(f"{' ' * padding}{Colors.CYAN}│{Colors.RESET}")
                            print(f"{Colors.CYAN}│{Colors.RESET}  ", end="", flush=True)
                            col = 2
                            if char != '\n':
                                print(char, end="", flush=True)
                                col += 1
                        else:
                            print(char, end="", flush=True)
                            col += 1

                # Close the line and box
                padding = width - col
                print(f"{' ' * padding}{Colors.CYAN}│{Colors.RESET}")
                print(f"{Colors.CYAN}│{Colors.RESET}{' ' * width}{Colors.CYAN}│{Colors.RESET}")
                print(f"{Colors.CYAN}╰{'─' * width}╯{Colors.RESET}")
                print()

                # Format sources
                if hasattr(response, 'source_nodes') and response.source_nodes:
                    source_lines = []
                    seen_files = set()
                    for node in response.source_nodes:
                        filename = node.metadata.get('file_name', 'Unknown')
                        if filename not in seen_files:
                            seen_files.add(filename)
                            score = node.score if hasattr(node, 'score') and node.score else 0
                            score_pct = int(score * 100) if score else 0
                            # Format: "  • filename (Relevance: XX%)"
                            # Max width inside box is 96 chars (100 - 2 padding on each side)
                            # "  • " = 4, " (Relevance: " = 13, "XX%)" = 4-5 chars
                            # So filename space = 96 - 4 - 13 - 5 = 74 chars
                            source_lines.append(f"  • {filename:<74}(Relevance: {score_pct}%)")

                    sources_content = '\n'.join(source_lines)
                    print_box("Sources", sources_content, Colors.BLUE)
            else:
                response = engine.chat(question)
                formatted_response = format_response_text(response.response)
                wrapped_content = wrap_text(formatted_response)
                print_box("Answer", wrapped_content, Colors.CYAN)

                # Format sources
                if hasattr(response, 'source_nodes') and response.source_nodes:
                    source_lines = []
                    seen_files = set()
                    for node in response.source_nodes:
                        filename = node.metadata.get('file_name', 'Unknown')
                        if filename not in seen_files:
                            seen_files.add(filename)
                            score = node.score if hasattr(node, 'score') and node.score else 0
                            score_pct = int(score * 100) if score else 0
                            # Format: "  • filename (Relevance: XX%)"
                            # Max width inside box is 96 chars (100 - 2 padding on each side)
                            # "  • " = 4, " (Relevance: " = 13, "XX%)" = 4-5 chars
                            # So filename space = 96 - 4 - 13 - 5 = 74 chars
                            source_lines.append(f"  • {filename:<74}(Relevance: {score_pct}%)")

                    sources_content = '\n'.join(source_lines)
                    print_box("Sources", sources_content, Colors.BLUE)

        except KeyboardInterrupt:
            print(f"\n\n{Colors.GREEN}👋 Goodbye!{Colors.RESET}")
            break
        except EOFError:
            print(f"\n{Colors.GREEN}👋 Goodbye!{Colors.RESET}")
            break
        except Exception as e:
            print(f"\n{Colors.YELLOW}✗ Error:{Colors.RESET} {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
