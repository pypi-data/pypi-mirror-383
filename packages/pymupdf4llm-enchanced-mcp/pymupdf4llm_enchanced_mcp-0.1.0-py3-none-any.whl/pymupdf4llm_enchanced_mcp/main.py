#!/usr/bin/env python3
"""MCP Server for PDF parsing and chunking with PyMuPDF4LLM and tiktoken.

This module implements a Model Context Protocol (MCP) server that provides
PDF parsing and chunking capabilities with intelligent caching and token-based
text segmentation using the stdio transport protocol.

The server exposes two main tools:
    - parse_pdf: Convert PDF to token-based markdown chunks with caching
    - read_chunk: Retrieve specific chunks from cache

Features:
    - SHA256-based file hashing for cache validation
    - Token-aware chunking with configurable overlap
    - Efficient caching to avoid redundant PDF processing
    - Full MCP protocol compliance with JSON-RPC 2.0
"""

from __future__ import annotations

import hashlib
import json
import logging
import sys
from pathlib import Path
from typing import Final

import pymupdf4llm  # type: ignore[import-untyped]
import tiktoken

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)


# Type aliases for clarity
JSONDict = dict[str, object]
ChunkList = list[str]

# Configuration constants
CACHE_DIR: Final[Path] = Path(".pymupdf4llm-enchanced-mcp")
ENCODING_NAME: Final[str] = "o200k_base"
HASH_CHUNK_SIZE: Final[int] = 8192

# JSON-RPC error codes
ERROR_PARSE: Final[int] = -32700
ERROR_METHOD_NOT_FOUND: Final[int] = -32601
ERROR_INTERNAL: Final[int] = -32000

# MCP protocol version
MCP_PROTOCOL_VERSION: Final[str] = "2024-11-05"
SERVER_NAME: Final[str] = "pymupdf4llm-enhanced-mcp"
SERVER_VERSION: Final[str] = "1.0.0"


class PDFProcessingError(Exception):
    """Raised when PDF parsing or processing fails."""


class CacheError(Exception):
    """Raised when cache operations fail."""


class ValidationError(Exception):
    """Raised when input validation fails."""


def compute_file_hash(file_path: str | Path) -> str:
    """Compute SHA256 hash of file content for cache validation.

    Args:
        file_path: Path to file to hash

    Returns:
        Hexadecimal SHA256 hash string

    Raises:
        FileNotFoundError: If file does not exist
        PermissionError: If file cannot be read
        OSError: For other I/O errors
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not path.is_file():
        raise ValidationError(f"Path is not a file: {file_path}")

    sha256 = hashlib.sha256()
    try:
        with path.open("rb") as f:
            while chunk := f.read(HASH_CHUNK_SIZE):
                sha256.update(chunk)
    except PermissionError as e:
        raise PermissionError(f"Cannot read file {file_path}: {e}") from e
    except OSError as e:
        raise OSError(f"Error reading file {file_path}: {e}") from e

    return sha256.hexdigest()


def get_cache_dir(
    file_path: str | Path,
    file_hash: str,
    chunk_size_tokens: int,
    chunk_overlap_tokens: int,
) -> Path:
    """Get cache directory path for a specific PDF file with chunking parameters.

    Creates a sanitized directory name based on the file path, hash, and
    chunking parameters to ensure unique cache locations per file version
    and chunking configuration.

    Args:
        file_path: Original PDF file path
        file_hash: SHA256 hash of the file content
        chunk_size_tokens: Maximum tokens per chunk
        chunk_overlap_tokens: Overlapping tokens between chunks

    Returns:
        Path to cache directory with format:
        {safe_path}_{short_hash}_{chunk_size}_{overlap}

    Example:
        >>> get_cache_dir("doc.pdf", "a1b2c3d4...", 1000, 100)
        Path('.pymupdf4llm-enchanced-mcp/doc.pdf_a1b2c3d4_1000_100')
    """
    # Sanitize file path for directory name
    safe_path = (
        str(file_path)
        .replace("/", "_")
        .replace("\\", "_")
        .replace("..", "_")
        .replace(" ", "_")
    )
    # Use first 8 characters of hash for readability
    short_hash = file_hash[:8]
    cache_name = f"{safe_path}_{short_hash}_{chunk_size_tokens}_{chunk_overlap_tokens}"
    return CACHE_DIR / cache_name


def validate_chunk_parameters(
    chunk_size: int,
    overlap: int,
) -> None:
    """Validate chunking parameters.

    Args:
        chunk_size: Maximum tokens per chunk
        overlap: Number of overlapping tokens between chunks

    Raises:
        ValidationError: If parameters are invalid
    """
    if chunk_size <= 0:
        raise ValidationError(f"chunk_size_tokens must be positive, got {chunk_size}")

    if overlap < 0:
        raise ValidationError(
            f"chunk_overlap_tokens must be non-negative, got {overlap}"
        )

    if overlap >= chunk_size:
        msg = (
            f"chunk_overlap_tokens ({overlap}) must be less than "
            f"chunk_size_tokens ({chunk_size})"
        )
        raise ValidationError(msg)


def chunk_by_tokens(
    text: str,
    chunk_size: int,
    overlap: int,
) -> ChunkList:
    """Split text into chunks based on token count with overlap.

    Uses tiktoken to count tokens accurately and creates overlapping chunks
    to maintain context across chunk boundaries.

    Args:
        text: Full markdown text to chunk
        chunk_size: Maximum tokens per chunk
        overlap: Number of overlapping tokens between chunks

    Returns:
        List of text chunks

    Raises:
        ValidationError: If parameters are invalid
        RuntimeError: If encoding fails
    """
    validate_chunk_parameters(chunk_size, overlap)

    try:
        encoding = tiktoken.get_encoding(ENCODING_NAME)
    except Exception as e:
        raise RuntimeError(f"Failed to load encoding {ENCODING_NAME}: {e}") from e

    try:
        tokens = encoding.encode(text)
    except Exception as e:
        raise RuntimeError(f"Failed to encode text: {e}") from e

    # If text fits in one chunk, return as-is
    if len(tokens) <= chunk_size:
        return [text]

    chunks: ChunkList = []
    step_size = chunk_size - overlap

    for i in range(0, len(tokens), step_size):
        chunk_tokens = tokens[i : i + chunk_size]
        try:
            chunk_text = encoding.decode(chunk_tokens)
            chunks.append(chunk_text)
        except Exception as e:
            logger.error(f"Failed to decode chunk at position {i}: {e}")
            continue

        # Break if we've covered all tokens
        if i + chunk_size >= len(tokens):
            break

    return chunks


def parse_pdf_tool(
    file_path: str,
    chunk_size_tokens: int,
    chunk_overlap_tokens: int,
) -> JSONDict:
    """Parse PDF file and create token-based markdown chunks with caching.

    Converts PDF to markdown, splits into token-based chunks with overlap,
    and caches results for efficient retrieval. Uses file hashing to detect
    changes and invalidate cache when needed.

    Args:
        file_path: Path to PDF file
        chunk_size_tokens: Maximum tokens per chunk
        chunk_overlap_tokens: Overlapping tokens between chunks

    Returns:
        Dictionary containing:
            - chunks_count: Number of chunks created
            - cached: Whether result was retrieved from cache

    Raises:
        ValidationError: If parameters or file path are invalid
        PDFProcessingError: If PDF parsing fails
        CacheError: If cache operations fail
    """
    # Validate file path
    path = Path(file_path)
    if not path.exists():
        raise ValidationError(f"File not found: {file_path}")
    if not path.is_file():
        raise ValidationError(f"Path is not a file: {file_path}")
    if not path.suffix.lower() == ".pdf":
        raise ValidationError(f"File is not a PDF: {file_path}")

    # Validate chunking parameters
    validate_chunk_parameters(chunk_size_tokens, chunk_overlap_tokens)

    # Compute file hash for cache key
    try:
        file_hash = compute_file_hash(file_path)
    except Exception as e:
        raise ValidationError(f"Cannot compute file hash: {e}") from e

    cache_dir = get_cache_dir(
        file_path, file_hash, chunk_size_tokens, chunk_overlap_tokens
    )

    # Check if cache exists and is valid
    if cache_dir.exists():
        chunk_files = sorted(cache_dir.glob("chunk_*.md"))
        if chunk_files:
            logger.debug(f"Cache hit for {file_path} (hash: {file_hash[:8]}...)")
            return {
                "chunks_count": len(chunk_files),
                "cached": True,
            }

    # Cache miss - process PDF
    logger.debug(f"Cache miss for {file_path}, processing PDF...")

    # Convert PDF to markdown
    try:
        markdown_text = pymupdf4llm.to_markdown(str(file_path))
    except Exception as e:
        raise PDFProcessingError(f"Failed to parse PDF {file_path}: {e}") from e

    if not markdown_text:
        raise PDFProcessingError("PDF parsing returned empty or invalid content")

    # Chunk by tokens
    try:
        chunks = chunk_by_tokens(
            markdown_text,
            chunk_size_tokens,
            chunk_overlap_tokens,
        )
    except Exception as e:
        raise PDFProcessingError(f"Failed to chunk text: {e}") from e

    # Create cache directory
    try:
        cache_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise CacheError(f"Failed to create cache directory: {e}") from e

    # Save chunks
    for idx, chunk in enumerate(chunks):
        chunk_file = cache_dir / f"chunk_{idx}.md"
        try:
            _ = chunk_file.write_text(chunk, encoding="utf-8")
        except OSError as e:
            raise CacheError(f"Failed to write chunk {idx}: {e}") from e

    logger.debug(f"Created {len(chunks)} chunks for {file_path}")

    return {
        "chunks_count": len(chunks),
        "cached": False,
    }


def read_chunk_tool(
    file_path: str,
    chunk_index: int,
    chunk_size_tokens: int,
    chunk_overlap_tokens: int,
) -> JSONDict:
    """Read a specific chunk from cache.

    Retrieves a previously generated markdown chunk based on the original
    PDF file path, chunk index, and chunking parameters. Requires parse_pdf
    to have been called first with the same chunking parameters to generate
    the cache.

    Args:
        file_path: Path to original PDF file
        chunk_index: Index of chunk to read (0-based)
        chunk_size_tokens: Maximum tokens per chunk used during parse_pdf
        chunk_overlap_tokens: Overlapping tokens used during parse_pdf

    Returns:
        Dictionary containing:
            - chunk_index: The requested chunk index
            - content: Markdown content of the chunk
            - file_path: Original PDF file path

    Raises:
        ValidationError: If file path, chunk index, or parameters are invalid
        CacheError: If cache not found or chunk doesn't exist
    """
    # Validate file path
    path = Path(file_path)
    if not path.exists():
        raise ValidationError(f"File not found: {file_path}")
    if not path.is_file():
        raise ValidationError(f"Path is not a file: {file_path}")

    # Validate chunk index
    if chunk_index < 0:
        raise ValidationError(f"chunk_index must be non-negative, got {chunk_index}")

    # Validate chunking parameters
    validate_chunk_parameters(chunk_size_tokens, chunk_overlap_tokens)

    # Compute file hash to find cache
    try:
        file_hash = compute_file_hash(file_path)
    except Exception as e:
        raise ValidationError(f"Cannot compute file hash: {e}") from e

    cache_dir = get_cache_dir(
        file_path, file_hash, chunk_size_tokens, chunk_overlap_tokens
    )

    if not cache_dir.exists():
        raise CacheError(f"No cache found for {file_path}. Run parse_pdf first.")

    # Read specific chunk
    chunk_file = cache_dir / f"chunk_{chunk_index}.md"

    if not chunk_file.exists():
        # Count available chunks for helpful error message
        chunk_files = sorted(cache_dir.glob("chunk_*.md"))
        max_index = len(chunk_files) - 1
        msg = (
            f"Chunk index {chunk_index} not found. "
            f"Valid range: 0-{max_index} ({len(chunk_files)} chunks available)"
        )
        raise CacheError(msg)

    try:
        content = chunk_file.read_text(encoding="utf-8")
    except OSError as e:
        raise CacheError(f"Failed to read chunk {chunk_index}: {e}") from e

    return {
        "chunk_index": chunk_index,
        "content": content,
        "file_path": file_path,
    }


# MCP Protocol Handlers


def handle_initialize(request_id: int | str | None, _params: JSONDict) -> JSONDict:
    """Handle MCP initialize request.

    Args:
        request_id: JSON-RPC request ID
        params: Request parameters (unused)

    Returns:
        JSON-RPC response with server capabilities
    """
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "protocolVersion": MCP_PROTOCOL_VERSION,
            "capabilities": {
                "tools": {},
            },
            "serverInfo": {
                "name": SERVER_NAME,
                "version": SERVER_VERSION,
            },
        },
    }


def handle_tools_list(request_id: int | str | None) -> JSONDict:
    """Handle MCP tools/list request.

    Args:
        request_id: JSON-RPC request ID

    Returns:
        JSON-RPC response with available tools and their schemas
    """
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "tools": [
                {
                    "name": "parse_pdf",
                    "description": (
                        "Parse PDF file into token-based markdown chunks with "
                        "intelligent caching. Returns chunk count and cache status."
                    ),
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to PDF file (must exist)",
                            },
                            "chunk_size_tokens": {
                                "type": "integer",
                                "description": (
                                    "Maximum number of tokens per chunk (must be positive)"
                                ),
                                "minimum": 1,
                            },
                            "chunk_overlap_tokens": {
                                "type": "integer",
                                "description": (
                                    "Number of overlapping tokens between chunks "
                                    "(must be less than chunk_size_tokens)"
                                ),
                                "minimum": 0,
                            },
                        },
                        "required": [
                            "file_path",
                            "chunk_size_tokens",
                            "chunk_overlap_tokens",
                        ],
                    },
                },
                {
                    "name": "read_chunk",
                    "description": (
                        "Read a specific markdown chunk from cache. "
                        "Requires parse_pdf to have been called first with the "
                        "same chunking parameters."
                    ),
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to original PDF file",
                            },
                            "chunk_index": {
                                "type": "integer",
                                "description": "Index of chunk to read (0-based)",
                                "minimum": 0,
                            },
                            "chunk_size_tokens": {
                                "type": "integer",
                                "description": (
                                    "Maximum number of tokens per chunk "
                                    "(must match parse_pdf parameters)"
                                ),
                                "minimum": 1,
                            },
                            "chunk_overlap_tokens": {
                                "type": "integer",
                                "description": (
                                    "Number of overlapping tokens between chunks "
                                    "(must match parse_pdf parameters)"
                                ),
                                "minimum": 0,
                            },
                        },
                        "required": [
                            "file_path",
                            "chunk_index",
                            "chunk_size_tokens",
                            "chunk_overlap_tokens",
                        ],
                    },
                },
            ],
        },
    }


def handle_tool_call(request_id: int | str | None, params: JSONDict) -> JSONDict:
    """Handle MCP tools/call request.

    Args:
        request_id: JSON-RPC request ID
        params: Request parameters containing tool name and arguments

    Returns:
        JSON-RPC response with tool result or error
    """
    tool_name = str(params.get("name", ""))
    arguments_raw = params.get("arguments", {})
    arguments = dict(arguments_raw) if isinstance(arguments_raw, dict) else {}

    try:
        if tool_name == "parse_pdf":
            result = parse_pdf_tool(
                file_path=str(arguments["file_path"]),
                chunk_size_tokens=int(arguments["chunk_size_tokens"]),
                chunk_overlap_tokens=int(arguments["chunk_overlap_tokens"]),
            )
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2),
                        }
                    ],
                },
            }

        elif tool_name == "read_chunk":
            result = read_chunk_tool(
                file_path=str(arguments["file_path"]),
                chunk_index=int(arguments["chunk_index"]),
                chunk_size_tokens=int(arguments["chunk_size_tokens"]),
                chunk_overlap_tokens=int(arguments["chunk_overlap_tokens"]),
            )
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": result["content"],
                        }
                    ],
                },
            }

        else:
            raise ValidationError(f"Unknown tool: {tool_name}")

    except (ValidationError, PDFProcessingError, CacheError) as e:
        logger.error(f"Tool call error ({type(e).__name__}): {e}")
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": ERROR_INTERNAL,
                "message": str(e),
                "data": {"error_type": type(e).__name__},
            },
        }
    except KeyError as e:
        logger.error(f"Missing required argument: {e}")
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": ERROR_INTERNAL,
                "message": f"Missing required argument: {e}",
            },
        }
    except Exception as e:
        logger.error(f"Unexpected error in tool call: {e}")
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": ERROR_INTERNAL,
                "message": f"Internal server error: {e}",
            },
        }


def handle_request(request: JSONDict) -> JSONDict:
    """Route MCP request to appropriate handler.

    Args:
        request: JSON-RPC request object

    Returns:
        JSON-RPC response object
    """
    method = request.get("method")
    request_id_raw = request.get("id")
    # Convert request_id to the expected type
    request_id: int | str | None = None
    if isinstance(request_id_raw, (int, str)):
        request_id = request_id_raw

    params_raw = request.get("params", {})
    params = dict(params_raw) if isinstance(params_raw, dict) else {}

    if method == "initialize":
        return handle_initialize(request_id, params)
    elif method == "tools/list":
        return handle_tools_list(request_id)
    elif method == "tools/call":
        return handle_tool_call(request_id, params)
    else:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": ERROR_METHOD_NOT_FOUND,
                "message": f"Method not found: {method}",
            },
        }


def main() -> None:
    """Main server loop - read from stdin, write to stdout.

    Implements the MCP stdio transport protocol by reading JSON-RPC requests
    from stdin and writing responses to stdout. Debug and error messages are
    logged to stderr to avoid interfering with the protocol.

    Exits with code 1 on fatal errors, 0 on clean shutdown (KeyboardInterrupt).
    """
    logger.debug(f"{SERVER_NAME} v{SERVER_VERSION} starting...")

    # Ensure cache directory exists
    try:
        CACHE_DIR.mkdir(exist_ok=True)
        logger.debug(f"Cache directory: {CACHE_DIR.absolute()}")
    except OSError as e:
        logger.error(f"Failed to create cache directory: {e}")
        sys.exit(1)

    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            try:
                request_raw = json.loads(line)
                request = dict(request_raw) if isinstance(request_raw, dict) else {}
                logger.debug(f"Received request: {request.get('method')}")

                response = handle_request(request)

                # Write response to stdout
                print(json.dumps(response), flush=True)

            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": ERROR_PARSE,
                        "message": "Parse error: Invalid JSON",
                    },
                }
                print(json.dumps(error_response), flush=True)

    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
