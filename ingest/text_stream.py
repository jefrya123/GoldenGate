"""
Text streaming functionality for binary file reading.
"""

from collections.abc import Iterator
from pathlib import Path


def iter_text_chunks(path: Path, chunk_bytes: int = 1_048_576) -> Iterator[str]:
    """
    Stream text chunks from a binary file with UTF-8 decoding.

    Args:
        path: Path to the text file
        chunk_bytes: Size of each chunk in bytes (default: 1MB)

    Yields:
        Text chunks as strings

    Raises:
        FileNotFoundError: If the file doesn't exist
        PermissionError: If the file can't be read
    """
    with open(path, "rb") as file:
        while True:
            chunk = file.read(chunk_bytes)
            if not chunk:
                break

            # Decode UTF-8 with error handling
            text = chunk.decode("utf-8", errors="ignore")
            if text.strip():  # Only yield non-empty chunks
                yield text
