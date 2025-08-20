"""
Ingest Package - File streaming and text extraction
"""

from .dispatch import iter_file_text
from .pdf_stream import SkippedEncryptedPDF, iter_pdf_pages
from .text_stream import iter_text_chunks

__version__ = "1.0.0"
__all__ = [
    "iter_text_chunks",
    "iter_pdf_pages",
    "SkippedEncryptedPDF",
    "iter_file_text",
]
