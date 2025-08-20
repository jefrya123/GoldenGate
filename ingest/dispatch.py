"""File dispatch functionality to route different file types to appropriate processors.

This module provides the main entry point for file content extraction, automatically
routing different file types to their specialized processors. It supports text files,
CSV, logs, markdown, HTML, and PDF files.
"""

from collections.abc import Iterator
from pathlib import Path

from .pdf_stream import iter_pdf_pages
from .text_stream import iter_text_chunks


def iter_file_text(
    path: Path,
    exts: set[str] = {".txt", ".csv", ".log", ".md", ".html", ".pdf"},
    text_chunk_bytes: int = 1_048_576,
    pdf_max_pages: int = 0,
) -> Iterator[str]:
    """Route file to appropriate text extraction method based on extension.

    This is the main dispatcher that examines file extensions and routes
    files to appropriate specialized processors for text extraction.

    Parameters
    ----------
    path : Path
        Path to the file to process.
    exts : set[str], optional
        Set of supported file extensions (default: common text and document formats).
    text_chunk_bytes : int, optional
        Size of text chunks for text files in bytes (default: 1MB).
    pdf_max_pages : int, optional
        Maximum pages to process for PDFs, 0 means all pages (default: 0).

    Yields
    ------
    str
        Text content extracted from the file in chunks.

    Raises
    ------
    ValueError
        If file extension is not in the supported set.
    FileNotFoundError
        If the specified file doesn't exist.
    PermissionError
        If the file can't be read due to permissions.
        
    Examples
    --------
    >>> from pathlib import Path
    >>> for text in iter_file_text(Path("document.pdf")):
    ...     print(text[:100])  # Process text chunks
    """
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    file_ext = path.suffix.lower()

    if file_ext not in exts:
        raise ValueError(f"Unsupported file extension: {file_ext}. Supported: {exts}")

    if file_ext == ".pdf":
        yield from iter_pdf_pages(path, max_pages=pdf_max_pages)
    else:
        # All other extensions are treated as text files
        yield from iter_text_chunks(path, chunk_bytes=text_chunk_bytes)


def extract_text_stream(path: Path, chunk_size: int = 10000) -> Iterator[str]:
    """Simple streaming text extraction for any file type.

    Provides a resilient text extraction interface with automatic fallback
    to plain text reading if specialized extraction fails.

    Parameters
    ----------
    path : Path
        Path to file to extract text from.
    chunk_size : int, optional
        Size of text chunks in characters (default: 10000).

    Yields
    ------
    str
        Text chunks extracted from the file.
        
    Notes
    -----
    This function includes fallback mechanisms:
    1. First attempts specialized extraction based on file type
    2. Falls back to plain text reading with UTF-8 encoding
    3. Silently handles failures to ensure robustness
    """
    try:
        # Use the existing dispatch function
        for text_chunk in iter_file_text(path, text_chunk_bytes=chunk_size):
            yield text_chunk
    except Exception as e:
        print(f"Warning: Could not extract text from {path}: {e}")
        # Fallback: try reading as plain text
        try:
            with open(path, encoding="utf-8", errors="ignore") as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
        except:
            pass  # Give up silently
