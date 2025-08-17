"""
Ingest Package - File streaming and text extraction
"""

from .text_stream import iter_text_chunks
from .pdf_stream import iter_pdf_pages, SkippedEncryptedPDF
from .dispatch import iter_file_text

__version__ = "1.0.0"
__all__ = ["iter_text_chunks", "iter_pdf_pages", "SkippedEncryptedPDF", "iter_file_text"] 