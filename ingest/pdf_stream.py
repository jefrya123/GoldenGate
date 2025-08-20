"""
PDF streaming functionality using pypdf.
"""

from collections.abc import Iterator
from pathlib import Path


class SkippedEncryptedPDF(Exception):
    """Raised when a PDF is encrypted and no password is provided."""

    pass


def iter_pdf_pages(path: Path, max_pages: int = 0) -> Iterator[str]:
    """
    Stream text from PDF pages using pypdf.

    Args:
        path: Path to the PDF file
        max_pages: Maximum number of pages to process (0 = all pages)

    Yields:
        Text content from each page

    Raises:
        FileNotFoundError: If the file doesn't exist
        PermissionError: If the file can't be read
        SkippedEncryptedPDF: If the PDF is encrypted and no password is provided
        ImportError: If pypdf is not installed
    """
    try:
        from pypdf import PdfReader
    except ImportError:
        raise ImportError(
            "pypdf is required for PDF processing. Install with: pip install pypdf"
        )

    try:
        reader = PdfReader(path)

        # Check if PDF is encrypted
        if reader.is_encrypted:
            try:
                # Try with empty password
                reader.decrypt("")
            except:
                raise SkippedEncryptedPDF(f"PDF is encrypted: {path}")

        # Determine number of pages to process
        total_pages = len(reader.pages)
        pages_to_process = (
            total_pages if max_pages == 0 else min(max_pages, total_pages)
        )

        for page_num in range(pages_to_process):
            try:
                page = reader.pages[page_num]
                text = page.extract_text()
                if text.strip():  # Only yield non-empty pages
                    yield text
            except Exception as e:
                # Skip problematic pages but continue processing
                print(
                    f"Warning: Could not extract text from page {page_num + 1} in {path}: {e}"
                )
                continue

    except SkippedEncryptedPDF:
        raise
    except Exception as e:
        raise Exception(f"Error processing PDF {path}: {e}")
