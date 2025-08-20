"""Pipeline functionality for scanning files and generating PII summaries.

This module provides the core pipeline for processing files through the PII
detection system, handling text extraction, entity detection, and result
aggregation.
"""

import json
from pathlib import Path

from ingest import iter_file_text
from pii import FileSummary, hits_from_text


def scan_file_once(
    path: Path,
    exts: set[str] | None = None,
    text_chunk_bytes: int = 1_048_576,
    pdf_max_pages: int = 0,
    chunk_size: int = 2000,
    overlap: int = 100,
    out_jsonl: Path | None = None,
) -> FileSummary:
    """Scan a file for PII entities and generate a summary.

    This is the main entry point for file scanning. It handles text extraction
    from various file formats, processes the text through PII detection, and
    aggregates results into a summary.

    Parameters
    ----------
    path : Path
        Path to the file to scan.
    exts : Set[str], optional
        Set of supported file extensions. Defaults to common text formats
        (.txt, .csv, .log, .md, .html, .pdf).
    text_chunk_bytes : int, optional
        Size of text chunks for reading large text files (default: 1MB).
    pdf_max_pages : int, optional
        Maximum pages to process for PDFs, 0 means all pages (default: 0).
    chunk_size : int, optional
        Size of text chunks for PII processing in characters (default: 2000).
    overlap : int, optional
        Character overlap between chunks to catch boundary entities (default: 100).
    out_jsonl : Path, optional
        Path to write detected entities as JSON lines for detailed analysis.

    Returns
    -------
    FileSummary
        Summary object containing counts and statistics of detected PII.

    Raises
    ------
    FileNotFoundError
        If the specified file doesn't exist.
    PermissionError
        If the file can't be read due to permissions.
    SkippedEncryptedPDF
        If a PDF file is encrypted and cannot be processed.
    ValueError
        If the file extension is not in the supported set.

    Notes
    -----
    The function uses streaming to handle large files efficiently without
    loading entire contents into memory. Results can optionally be written
    to a JSONL file for detailed entity-level analysis.
    """
    # Default supported extensions
    if exts is None:
        exts = {".txt", ".csv", ".log", ".md", ".html", ".pdf"}

    # Initialize counters (memory-efficient)
    total_count = 0
    controlled_count = 0
    noncontrolled_count = 0
    entity_type_counts = {}

    # Open JSONL output file if specified
    jsonl_file = None
    if out_jsonl:
        jsonl_file = open(out_jsonl, "w", encoding="utf-8")

    try:
        # Stream text blocks from the file
        for text_block in iter_file_text(
            path=path,
            exts=exts,
            text_chunk_bytes=text_chunk_bytes,
            pdf_max_pages=pdf_max_pages,
        ):
            # Process each text block for PII
            hits = hits_from_text(
                text=text_block, chunk_size=chunk_size, overlap=overlap
            )

            # Update counters (don't store hits in memory)
            for hit in hits:
                total_count += 1
                if hit.label == "Controlled":
                    controlled_count += 1
                elif hit.label == "NonControlled":
                    noncontrolled_count += 1

                # Count entity types
                entity_type_counts[hit.entity_type] = (
                    entity_type_counts.get(hit.entity_type, 0) + 1
                )

                # Write to JSONL if specified
                if jsonl_file:
                    hit_dict = {
                        "entity_type": hit.entity_type,
                        "value": hit.value,
                        "start": hit.start,
                        "end": hit.end,
                        "score": hit.score,
                        "label": hit.label,
                        "context_left": hit.context_left,
                        "context_right": hit.context_right,
                    }
                    jsonl_file.write(json.dumps(hit_dict) + "\n")
                    jsonl_file.flush()  # Ensure immediate writing

            # Clear hits from memory after processing
            del hits

    finally:
        # Close JSONL file if open
        if jsonl_file:
            jsonl_file.close()

    # Generate summary
    summary = FileSummary(
        total=total_count,
        controlled=controlled_count,
        noncontrolled=noncontrolled_count,
        top_types=entity_type_counts,
    )

    # Sort top types by count (descending)
    summary.top_types = dict(
        sorted(summary.top_types.items(), key=lambda x: x[1], reverse=True)
    )

    return summary
