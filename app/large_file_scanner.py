"""
Universal large file scanner with intelligent processing for ANY file type.
Handles CSV, TXT, PDF, JSON, XML, logs, and more with automatic optimization.
"""

import gc
import mmap
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from app.parallel_scanner import MemoryManager, _process_text_chunk
from app.progress import ProgressMonitor, ProgressTracker
from ingest.csv_stream import StreamingCSVProcessor
from ingest.dispatch import extract_text_stream
from pii.engine import hits_from_text


class UniversalLargeFileScanner:
    """
    Universal scanner for ANY large file type with automatic optimization.
    Intelligently handles text files, CSVs, PDFs, logs, JSON, XML, etc.
    """

    def __init__(
        self, max_workers: int | None = None, max_memory_mb: int | None = None
    ):
        """
        Initialize universal file scanner.

        Args:
            max_workers: Maximum worker processes (auto-detected if None)
            max_memory_mb: Maximum memory usage in MB (auto-detected if None)
        """
        self.memory_manager = MemoryManager()
        self.max_workers = max_workers or self.memory_manager.get_optimal_workers()
        # Auto-calculate memory limit (80% of available RAM)
        if max_memory_mb is None:
            import psutil

            total_mb = psutil.virtual_memory().total / (1024 * 1024)
            self.max_memory_mb = int(total_mb * 0.8)
        else:
            self.max_memory_mb = max_memory_mb

        print(
            f"🚀 Universal Scanner initialized: {self.max_workers} workers, {self.max_memory_mb}MB memory limit"
        )

    def scan_file(self, file_path: Path, out_dir: Path) -> dict[str, Any]:
        """
        Intelligently scan ANY large file with automatic optimization.

        Args:
            file_path: Path to file (any type)
            out_dir: Output directory

        Returns:
            Scan results with statistics
        """
        print(f"\n🔍 Analyzing file: {file_path.name}")

        # Get file info and choose strategy
        file_info = self._analyze_file(file_path)
        print(
            f"📊 File: {file_info['size_mb']:.1f} MB, Type: {file_info['type']}, Strategy: {file_info['strategy']}"
        )

        # Create progress tracker
        operation_id = f"scan_{file_path.name}_{int(time.time())}"
        tracker = ProgressTracker(operation_id)

        if file_info["estimated_chunks"]:
            tracker.set_total(file_info["estimated_chunks"])

        # Start progress monitoring
        monitor = ProgressMonitor(tracker, update_interval=0.5)
        monitor.start()

        try:
            # Choose scanning strategy based on file analysis
            if file_info["strategy"] == "csv_streaming":
                result = self._scan_csv_streaming(file_path, tracker, file_info)
            elif file_info["strategy"] == "memory_mapped":
                result = self._scan_memory_mapped(file_path, tracker, file_info)
            elif file_info["strategy"] == "chunked_streaming":
                result = self._scan_chunked_streaming(file_path, tracker, file_info)
            elif file_info["strategy"] == "parallel_chunks":
                result = self._scan_parallel_chunks(file_path, tracker, file_info)
            else:
                # Fallback to standard processing
                result = self._scan_standard(file_path, tracker, file_info)

            monitor.stop()
            tracker.finish()

            return result

        except Exception as e:
            monitor.stop()
            print(f"\n❌ Error scanning file: {e}")
            return {
                "error": str(e),
                "entities": [],
                "stats": tracker.get_stats(),
                "file_info": file_info,
            }

    def _analyze_file(self, file_path: Path) -> dict[str, Any]:
        """
        Analyze file to determine optimal processing strategy.

        Returns:
            Dictionary with file analysis and recommended strategy
        """
        try:
            file_size = file_path.stat().st_size
            file_size_mb = file_size / (1024 * 1024)
            available_memory_mb = self.memory_manager.get_available_memory_mb()

            # Analyze file type and content
            file_ext = file_path.suffix.lower()

            # Quick content sampling for text files
            is_structured = False
            is_binary = False
            sample_lines = 0

            try:
                with open(file_path, "rb") as f:
                    sample = f.read(8192)  # 8KB sample

                # Check if binary
                if b"\x00" in sample:
                    is_binary = True
                else:
                    # Decode and analyze text
                    try:
                        text_sample = sample.decode("utf-8", errors="ignore")
                        sample_lines = text_sample.count("\n")

                        # Check for structured data
                        if (
                            file_ext == ".csv"
                            or "," in text_sample[:1000]
                            and sample_lines > 5
                        ):
                            is_structured = True
                        elif file_ext in [".json", ".xml"]:
                            is_structured = True

                    except (UnicodeDecodeError, AttributeError):
                        is_binary = True
            except (OSError, IOError):
                is_binary = True

            # Estimate processing chunks
            estimated_chunks = max(int(file_size_mb / 5), 1)  # ~5MB per chunk estimate

            # Choose strategy based on analysis
            strategy = self._choose_strategy(
                file_size_mb,
                available_memory_mb,
                file_ext,
                is_structured,
                is_binary,
                sample_lines,
            )

            # Calculate optimal chunk size
            chunk_size = self.memory_manager.get_optimal_chunk_size(file_size_mb)

            return {
                "file_path": str(file_path),
                "size_bytes": file_size,
                "size_mb": file_size_mb,
                "type": file_ext,
                "is_structured": is_structured,
                "is_binary": is_binary,
                "available_memory_mb": available_memory_mb,
                "estimated_chunks": estimated_chunks,
                "strategy": strategy,
                "optimal_chunk_size": chunk_size,
                "sample_lines": sample_lines,
            }

        except Exception as e:
            return {
                "error": str(e),
                "file_path": str(file_path),
                "strategy": "standard",
            }

    def _choose_strategy(
        self,
        file_size_mb: float,
        available_memory_mb: float,
        file_ext: str,
        is_structured: bool,
        is_binary: bool,
        sample_lines: int,
    ) -> str:
        """Choose optimal processing strategy based on file characteristics."""

        # Binary files (PDFs, etc.) - use standard extraction
        if is_binary:
            if file_size_mb > 100:
                return "chunked_streaming"
            else:
                return "standard"

        # Large CSV files - use streaming
        if file_ext == ".csv" and file_size_mb > 50:
            return "csv_streaming"

        # Very large text files - use memory mapping if possible
        if file_size_mb > 500 and not is_structured:
            if file_size_mb < available_memory_mb * 0.5:  # Can fit in memory
                return "memory_mapped"
            else:
                return "parallel_chunks"

        # Large text files - use parallel processing
        if file_size_mb > 100:
            return "parallel_chunks"

        # Medium files - use chunked streaming
        if file_size_mb > 20:
            return "chunked_streaming"

        # Small files - standard processing
        return "standard"

    def _scan_csv_streaming(
        self, file_path: Path, tracker: ProgressTracker, file_info: dict
    ) -> dict[str, Any]:
        """Scan CSV using streaming processor."""
        print("📊 Using CSV streaming strategy...")

        all_entities = []
        csv_processor = StreamingCSVProcessor(file_path, self.max_memory_mb // 2)

        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []

            for text_chunk in csv_processor.stream_concatenated_text(
                chunk_rows=2000, max_chars=file_info["optimal_chunk_size"]
            ):
                if text_chunk.strip():
                    future = executor.submit(_process_text_chunk, text_chunk, 4000, 200)
                    futures.append(future)

                    # Update progress
                    rows_processed, total_rows, _ = csv_processor.get_progress()
                    tracker.update(
                        processed=1, bytes_count=len(text_chunk.encode("utf-8"))
                    )

                    # Collect results periodically
                    if len(futures) >= self.max_workers * 2:
                        self._collect_futures(futures, all_entities, tracker)

            # Collect remaining results
            self._collect_futures(futures, all_entities, tracker)

        return self._build_result(all_entities, tracker, file_info)

    def _scan_memory_mapped(
        self, file_path: Path, tracker: ProgressTracker, file_info: dict
    ) -> dict[str, Any]:
        """Scan using memory mapping for very large text files."""
        print("🗺️  Using memory-mapped strategy...")

        all_entities = []
        chunk_size = file_info["optimal_chunk_size"]

        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mmapped_file:

                    with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                        futures = []
                        position = 0

                        while position < len(mmapped_file):
                            # Read chunk
                            end_pos = min(position + chunk_size, len(mmapped_file))
                            chunk_bytes = mmapped_file[position:end_pos]

                            try:
                                text_chunk = chunk_bytes.decode(
                                    "utf-8", errors="ignore"
                                )

                                if text_chunk.strip():
                                    future = executor.submit(
                                        _process_text_chunk, text_chunk, 4000, 200
                                    )
                                    futures.append(future)

                                    tracker.update(
                                        processed=1, bytes_count=len(chunk_bytes)
                                    )

                                    # Collect results periodically
                                    if len(futures) >= self.max_workers * 2:
                                        self._collect_futures(
                                            futures, all_entities, tracker
                                        )

                                position = end_pos

                            except UnicodeDecodeError:
                                position += 1000  # Skip problematic section

                        # Collect remaining results
                        self._collect_futures(futures, all_entities, tracker)

        except Exception as e:
            print(f"Memory mapping failed, falling back: {e}")
            return self._scan_chunked_streaming(file_path, tracker, file_info)

        return self._build_result(all_entities, tracker, file_info)

    def _scan_chunked_streaming(
        self, file_path: Path, tracker: ProgressTracker, file_info: dict
    ) -> dict[str, Any]:
        """Scan using chunked streaming for medium-large files."""
        print("🌊 Using chunked streaming strategy...")

        all_entities = []
        chunk_size = file_info["optimal_chunk_size"]

        try:
            # Use existing text extraction
            for text_chunk in extract_text_stream(file_path, chunk_size):
                if text_chunk.strip():
                    entities = hits_from_text(text_chunk, 4000, 200)
                    all_entities.extend(entities)

                    # Update progress
                    controlled = sum(1 for e in entities if e.label == "Controlled")
                    noncontrolled = len(entities) - controlled

                    tracker.update(
                        processed=1,
                        entities=len(entities),
                        controlled=controlled,
                        noncontrolled=noncontrolled,
                        bytes_count=len(text_chunk.encode("utf-8")),
                    )

                    # Memory cleanup
                    if tracker.processed_items % 10 == 0:
                        self.memory_manager.cleanup_if_needed()

        except Exception as e:
            print(f"Chunked streaming error: {e}")

        return self._build_result(all_entities, tracker, file_info)

    def _scan_parallel_chunks(
        self, file_path: Path, tracker: ProgressTracker, file_info: dict
    ) -> dict[str, Any]:
        """Scan using parallel chunk processing for very large files."""
        print("⚡ Using parallel chunks strategy...")

        all_entities = []
        chunk_size = file_info["optimal_chunk_size"]

        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []

            try:
                for text_chunk in extract_text_stream(file_path, chunk_size):
                    if text_chunk.strip():
                        future = executor.submit(
                            _process_text_chunk, text_chunk, 4000, 200
                        )
                        futures.append(future)

                        tracker.update(
                            processed=1, bytes_count=len(text_chunk.encode("utf-8"))
                        )

                        # Collect results periodically
                        if len(futures) >= self.max_workers * 3:
                            self._collect_futures(futures, all_entities, tracker)

                # Collect remaining results
                self._collect_futures(futures, all_entities, tracker)

            except Exception as e:
                print(f"Parallel processing error: {e}")

        return self._build_result(all_entities, tracker, file_info)

    def _scan_standard(
        self, file_path: Path, tracker: ProgressTracker, file_info: dict
    ) -> dict[str, Any]:
        """Standard processing for smaller files."""
        print("📄 Using standard strategy...")

        try:
            # Extract all text at once for smaller files
            all_text = ""
            for text_chunk in extract_text_stream(
                file_path, file_info.get("optimal_chunk_size", 10000)
            ):
                all_text += text_chunk + "\n"

            # Process all at once
            entities = hits_from_text(all_text, 4000, 200)

            # Update tracker
            controlled = sum(1 for e in entities if e.label == "Controlled")
            noncontrolled = len(entities) - controlled

            tracker.update(
                processed=1,
                entities=len(entities),
                controlled=controlled,
                noncontrolled=noncontrolled,
                bytes_count=len(all_text.encode("utf-8")),
            )

            return self._build_result(entities, tracker, file_info)

        except Exception as e:
            print(f"Standard processing error: {e}")
            return self._build_result([], tracker, file_info)

    def _collect_futures(
        self, futures: list, all_entities: list, tracker: ProgressTracker
    ):
        """Collect results from completed futures."""
        completed = []

        for future in as_completed(futures, timeout=0.1):
            try:
                entities = future.result()
                all_entities.extend(entities)

                # Update tracker
                controlled = sum(1 for e in entities if e.label == "Controlled")
                noncontrolled = len(entities) - controlled

                tracker.update(
                    entities=len(entities),
                    controlled=controlled,
                    noncontrolled=noncontrolled,
                )

                completed.append(future)

            except Exception as e:
                print(f"Warning: Chunk failed: {e}")
                completed.append(future)

        # Remove completed futures
        for future in completed:
            if future in futures:
                futures.remove(future)

        # Memory cleanup
        if len(completed) > 0:
            gc.collect()

    def _build_result(
        self, entities: list, tracker: ProgressTracker, file_info: dict
    ) -> dict[str, Any]:
        """Build final result dictionary."""
        stats = tracker.get_stats()

        return {
            "entities": entities,
            "stats": stats,
            "file_info": file_info,
            "summary": {
                "total_entities": len(entities),
                "controlled": sum(1 for e in entities if e.label == "Controlled"),
                "noncontrolled": sum(1 for e in entities if e.label != "Controlled"),
                "processing_time": stats["elapsed_seconds"],
                "throughput_mb_per_sec": file_info.get("size_mb", 0)
                / max(stats["elapsed_seconds"], 0.1),
            },
        }
