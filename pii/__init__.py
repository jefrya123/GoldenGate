"""
PII Detection Package - Enhanced Presidio Integration with Simplified US vs Foreign Classification
"""

from .classifier import classify_label
from .engine import hits_from_text
from .schema import EntityHit, FileSummary, summarize

__version__ = "1.0.0"
__all__ = ["EntityHit", "FileSummary", "summarize", "hits_from_text", "classify_label"]
