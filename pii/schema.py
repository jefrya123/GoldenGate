"""
PII Data Schema and Summary Functions
"""

from dataclasses import dataclass
from typing import Literal


@dataclass
class EntityHit:
    """Represents a detected PII entity."""

    entity_type: str
    value: str
    start: int
    end: int
    score: float
    label: Literal["Controlled", "NonControlled"]
    context_left: str
    context_right: str


@dataclass
class FileSummary:
    """Summary statistics for PII detection results."""

    total: int
    controlled: int
    noncontrolled: int
    top_types: dict[str, int]


def summarize(hits: list[EntityHit]) -> FileSummary:
    """
    Generate summary statistics from a list of entity hits.

    Args:
        hits: List of detected entities

    Returns:
        FileSummary with statistics
    """
    total = len(hits)
    controlled = sum(1 for hit in hits if hit.label == "Controlled")
    noncontrolled = total - controlled

    # Count entity types
    type_counts = {}
    for hit in hits:
        type_counts[hit.entity_type] = type_counts.get(hit.entity_type, 0) + 1

    # Sort by count (descending) and take top types
    top_types = dict(sorted(type_counts.items(), key=lambda x: x[1], reverse=True))

    return FileSummary(
        total=total,
        controlled=controlled,
        noncontrolled=noncontrolled,
        top_types=top_types,
    )
