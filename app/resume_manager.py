"""
Intelligent resume manager for interrupted large file scans.
Automatically detects interruptions and resumes from last checkpoint.
"""

import fcntl
import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any


class ResumeManager:
    """Smart resume manager that automatically handles scan interruptions."""

    def __init__(self, output_dir: Path):
        """
        Initialize resume manager.

        Args:
            output_dir: Output directory for scan results
        """
        self.output_dir = output_dir
        self.resume_dir = output_dir / ".resume"
        self.resume_dir.mkdir(exist_ok=True)

        # Lock file to prevent concurrent scans
        self.lock_file = self.resume_dir / "scan.lock"
        self.lock_fd = None

    def acquire_lock(self, operation_id: str) -> bool:
        """
        Acquire exclusive lock for scanning operation.

        Args:
            operation_id: Unique operation identifier

        Returns:
            True if lock acquired, False if another scan is running
        """
        try:
            self.lock_fd = open(self.lock_file, "w")
            fcntl.flock(self.lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

            # Write operation info to lock file
            lock_info = {
                "operation_id": operation_id,
                "pid": os.getpid(),
                "start_time": datetime.now().isoformat(),
                "hostname": os.uname().nodename if hasattr(os, "uname") else "unknown",
            }

            json.dump(lock_info, self.lock_fd, indent=2)
            self.lock_fd.flush()

            return True

        except OSError:
            if self.lock_fd:
                self.lock_fd.close()
                self.lock_fd = None
            return False

    def release_lock(self):
        """Release scanning lock."""
        if self.lock_fd:
            try:
                fcntl.flock(self.lock_fd.fileno(), fcntl.LOCK_UN)
                self.lock_fd.close()
                self.lock_file.unlink(missing_ok=True)
            except (OSError, AttributeError):
                pass
            finally:
                self.lock_fd = None

    def get_file_fingerprint(self, file_path: Path) -> str:
        """
        Generate unique fingerprint for file based on path, size, and mtime.

        Args:
            file_path: Path to file

        Returns:
            Unique fingerprint string
        """
        try:
            stat = file_path.stat()
            fingerprint_data = f"{file_path}:{stat.st_size}:{stat.st_mtime}"
            return hashlib.md5(fingerprint_data.encode()).hexdigest()[:16]
        except (OSError, FileNotFoundError):
            # Fallback to path-based fingerprint
            return hashlib.md5(str(file_path).encode()).hexdigest()[:16]

    def save_checkpoint(self, file_path: Path, progress_data: dict[str, Any]) -> Path:
        """
        Save progress checkpoint for file.

        Args:
            file_path: File being processed
            progress_data: Current progress information

        Returns:
            Path to checkpoint file
        """
        fingerprint = self.get_file_fingerprint(file_path)
        checkpoint_file = self.resume_dir / f"checkpoint_{fingerprint}.json"

        checkpoint_data = {
            "file_path": str(file_path),
            "fingerprint": fingerprint,
            "save_time": datetime.now().isoformat(),
            "progress": progress_data,
            "version": "1.0",
        }

        try:
            # Atomic write using temporary file
            temp_file = checkpoint_file.with_suffix(".tmp")
            with open(temp_file, "w") as f:
                json.dump(checkpoint_data, f, indent=2)

            temp_file.replace(checkpoint_file)
            return checkpoint_file

        except Exception as e:
            print(f"Warning: Could not save checkpoint: {e}")
            return checkpoint_file

    def load_checkpoint(self, file_path: Path) -> dict[str, Any] | None:
        """
        Load progress checkpoint for file.

        Args:
            file_path: File to check for checkpoint

        Returns:
            Checkpoint data if available and valid, None otherwise
        """
        fingerprint = self.get_file_fingerprint(file_path)
        checkpoint_file = self.resume_dir / f"checkpoint_{fingerprint}.json"

        if not checkpoint_file.exists():
            return None

        try:
            with open(checkpoint_file) as f:
                checkpoint_data = json.load(f)

            # Validate checkpoint
            if self._is_checkpoint_valid(checkpoint_data, file_path):
                return checkpoint_data
            else:
                # Invalid checkpoint, remove it
                checkpoint_file.unlink(missing_ok=True)
                return None

        except Exception as e:
            print(f"Warning: Could not load checkpoint: {e}")
            # Remove corrupted checkpoint
            checkpoint_file.unlink(missing_ok=True)
            return None

    def _is_checkpoint_valid(self, checkpoint_data: dict, file_path: Path) -> bool:
        """
        Validate checkpoint data against current file state.

        Args:
            checkpoint_data: Loaded checkpoint data
            file_path: Current file path

        Returns:
            True if checkpoint is valid for current file state
        """
        try:
            # Check if file path matches
            if checkpoint_data.get("file_path") != str(file_path):
                return False

            # Check if fingerprint matches (file unchanged)
            current_fingerprint = self.get_file_fingerprint(file_path)
            if checkpoint_data.get("fingerprint") != current_fingerprint:
                return False

            # Check if checkpoint is not too old (optional)
            save_time_str = checkpoint_data.get("save_time", "")
            if save_time_str:
                save_time = datetime.fromisoformat(save_time_str)
                age_hours = (datetime.now() - save_time).total_seconds() / 3600

                # Consider checkpoint stale after 24 hours
                if age_hours > 24:
                    return False

            return True

        except (OSError, json.JSONDecodeError, KeyError):
            return False

    def clear_checkpoint(self, file_path: Path):
        """
        Clear checkpoint for completed file.

        Args:
            file_path: File that was completed
        """
        fingerprint = self.get_file_fingerprint(file_path)
        checkpoint_file = self.resume_dir / f"checkpoint_{fingerprint}.json"
        checkpoint_file.unlink(missing_ok=True)

    def list_pending_checkpoints(self) -> list[dict[str, Any]]:
        """
        List all pending checkpoints that can be resumed.

        Returns:
            List of checkpoint information
        """
        pending = []

        for checkpoint_file in self.resume_dir.glob("checkpoint_*.json"):
            try:
                with open(checkpoint_file) as f:
                    checkpoint_data = json.load(f)

                file_path = Path(checkpoint_data.get("file_path", ""))

                # Check if file still exists and checkpoint is valid
                if file_path.exists() and self._is_checkpoint_valid(
                    checkpoint_data, file_path
                ):
                    pending.append(
                        {
                            "file_path": str(file_path),
                            "fingerprint": checkpoint_data.get("fingerprint"),
                            "save_time": checkpoint_data.get("save_time"),
                            "progress": checkpoint_data.get("progress", {}),
                            "checkpoint_file": str(checkpoint_file),
                        }
                    )
                else:
                    # Clean up invalid checkpoints
                    checkpoint_file.unlink(missing_ok=True)

            except Exception as e:
                print(f"Warning: Could not read checkpoint {checkpoint_file}: {e}")
                # Clean up corrupted checkpoint
                checkpoint_file.unlink(missing_ok=True)

        # Sort by save time (newest first)
        pending.sort(key=lambda x: x.get("save_time", ""), reverse=True)
        return pending

    def cleanup_old_checkpoints(self, max_age_hours: int = 48):
        """
        Clean up old checkpoint files.

        Args:
            max_age_hours: Maximum age of checkpoints to keep
        """
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)

        for checkpoint_file in self.resume_dir.glob("checkpoint_*.json"):
            try:
                if checkpoint_file.stat().st_mtime < cutoff_time:
                    checkpoint_file.unlink()
            except (OSError, FileNotFoundError):
                pass

    def get_scan_status(self) -> dict[str, Any]:
        """
        Get current scanning status.

        Returns:
            Dictionary with scanning status information
        """
        status = {
            "is_locked": self.lock_file.exists(),
            "pending_checkpoints": len(self.list_pending_checkpoints()),
            "resume_dir": str(self.resume_dir),
        }

        # Get lock info if available
        if status["is_locked"]:
            try:
                with open(self.lock_file) as f:
                    lock_info = json.load(f)
                status["current_operation"] = lock_info
            except (OSError, json.JSONDecodeError):
                status["current_operation"] = None

        return status


class SmartResumeScanner:
    """
    Scanner wrapper that automatically handles resume functionality.
    """

    def __init__(self, output_dir: Path):
        """Initialize smart resume scanner."""
        self.output_dir = output_dir
        self.resume_manager = ResumeManager(output_dir)

    def scan_with_resume(
        self, file_path: Path, scanner_func, operation_id: str = None
    ) -> dict[str, Any]:
        """
        Scan file with automatic resume capability.

        Args:
            file_path: File to scan
            scanner_func: Function that performs the actual scanning
            operation_id: Optional operation ID

        Returns:
            Scan results
        """
        if not operation_id:
            operation_id = f"scan_{file_path.name}_{int(datetime.now().timestamp())}"

        # Acquire lock
        if not self.resume_manager.acquire_lock(operation_id):
            return {
                "error": "Another scan is already in progress",
                "status": self.resume_manager.get_scan_status(),
            }

        try:
            # Check for existing checkpoint
            checkpoint = self.resume_manager.load_checkpoint(file_path)

            if checkpoint:
                print(f"📂 Found checkpoint for {file_path.name}, resuming...")
                progress_data = checkpoint.get("progress", {})
            else:
                print(f"🆕 Starting new scan of {file_path.name}")
                progress_data = {}

            # Perform scan with resume data
            result = scanner_func(file_path, self.output_dir, progress_data)

            # Clear checkpoint on successful completion
            self.resume_manager.clear_checkpoint(file_path)

            return result

        except KeyboardInterrupt:
            print(f"\n⏸️  Scan interrupted, checkpoint saved for {file_path.name}")
            # Checkpoint should already be saved by scanner_func
            raise

        except Exception as e:
            print(f"❌ Scan failed: {e}")
            return {"error": str(e)}

        finally:
            self.resume_manager.release_lock()

    def list_resumable_scans(self) -> list[dict[str, Any]]:
        """List all scans that can be resumed."""
        return self.resume_manager.list_pending_checkpoints()

    def cleanup_old_data(self):
        """Clean up old checkpoint data."""
        self.resume_manager.cleanup_old_checkpoints()
