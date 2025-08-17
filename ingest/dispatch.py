"""
File dispatch functionality to route different file types to appropriate processors.
"""

from typing import Iterator, Set
from pathlib import Path
from .text_stream import iter_text_chunks
from .pdf_stream import iter_pdf_pages


def iter_file_text(
    path: Path, 
    exts: Set[str] = {'.txt', '.csv', '.log', '.md', '.html', '.pdf'},
    text_chunk_bytes: int = 1_048_576,
    pdf_max_pages: int = 0
) -> Iterator[str]:
    """
    Route file to appropriate text extraction method based on extension.
    
    Args:
        path: Path to the file
        exts: Set of supported file extensions
        text_chunk_bytes: Size of text chunks for text files
        pdf_max_pages: Maximum pages to process for PDFs (0 = all)
        
    Yields:
        Text content from the file
        
    Raises:
        ValueError: If file extension is not supported
        FileNotFoundError: If the file doesn't exist
        PermissionError: If the file can't be read
    """
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    file_ext = path.suffix.lower()
    
    if file_ext not in exts:
        raise ValueError(f"Unsupported file extension: {file_ext}. Supported: {exts}")
    
    if file_ext == '.pdf':
        yield from iter_pdf_pages(path, max_pages=pdf_max_pages)
    else:
        # All other extensions are treated as text files
        yield from iter_text_chunks(path, chunk_bytes=text_chunk_bytes)

def extract_text_stream(path: Path, chunk_size: int = 10000) -> Iterator[str]:
    """
    Simple streaming text extraction for any file type.
    
    Args:
        path: Path to file
        chunk_size: Size of text chunks
        
    Yields:
        Text chunks from the file
    """
    try:
        # Use the existing dispatch function
        for text_chunk in iter_file_text(path, text_chunk_bytes=chunk_size):
            yield text_chunk
    except Exception as e:
        print(f"Warning: Could not extract text from {path}: {e}")
        # Fallback: try reading as plain text
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
        except:
            pass  # Give up silently 