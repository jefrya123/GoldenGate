"""PII Detection Engine - Enhanced Presidio Integration.

This module provides the core PII detection engine built on top of Microsoft
Presidio. It includes custom recognizers for various PII types and enhanced
filtering to reduce false positives.
"""

import re
import sys
from pathlib import Path

from presidio_analyzer import (
    AnalyzerEngine,
    Pattern,
    PatternRecognizer,
    RecognizerResult,
)
from presidio_analyzer.nlp_engine import NlpArtifacts, NlpEngineProvider

from .classifier import classify_label
from .schema import EntityHit

# Add parent to path for config import
sys.path.append(str(Path(__file__).parent.parent))
from config import FEATURES


class EnhancedRobustRecognizer(PatternRecognizer):
    """Enhanced pattern recognizer with overlapping result filtering.

    Extends Presidio's PatternRecognizer to provide better handling of
    overlapping matches and duplicate detection, ensuring cleaner results.

    Attributes
    ----------
    entity_type : str
        The type of entity this recognizer detects (e.g., 'ID', 'CREDIT_CARD').
    patterns : List[Pattern]
        List of regex patterns used for detection.
    """

    def __init__(self, entity_type: str, patterns: list[Pattern]):
        """Initialize the enhanced recognizer.

        Parameters
        ----------
        entity_type : str
            The entity type this recognizer will detect.
        patterns : List[Pattern]
            List of compiled regex patterns for matching.
        """
        super().__init__(
            supported_entity=entity_type, patterns=patterns, supported_language="en"
        )

    def analyze(
        self, text: str, entities: list[str], nlp_artifacts: NlpArtifacts
    ) -> list[RecognizerResult]:
        """Analyze text for PII with enhanced filtering.

        Parameters
        ----------
        text : str
            The text to analyze for PII.
        entities : List[str]
            List of entity types to look for.
        nlp_artifacts : NlpArtifacts
            NLP processing artifacts from spaCy.

        Returns
        -------
        List[RecognizerResult]
            List of detected entities with overlaps filtered out.
        """
        results = super().analyze(text, entities, nlp_artifacts)

        # Remove duplicates and overlapping results
        filtered_results = self._filter_overlapping_results(results)

        return filtered_results

    def _filter_overlapping_results(
        self, results: list[RecognizerResult]
    ) -> list[RecognizerResult]:
        """Remove overlapping detections, keeping highest confidence matches.

        Parameters
        ----------
        results : List[RecognizerResult]
            Raw detection results that may contain overlaps.

        Returns
        -------
        List[RecognizerResult]
            Filtered results with overlaps removed.
        """
        if not results:
            return results

        sorted_results = sorted(results, key=lambda x: x.score, reverse=True)
        filtered = []

        for result in sorted_results:
            overlaps = False
            for accepted in filtered:
                if result.start < accepted.end and result.end > accepted.start:
                    overlaps = True
                    break

            if not overlaps:
                filtered.append(result)

        return filtered


def build_analyzer() -> AnalyzerEngine | None:
    """
    Build Presidio analyzer with enhanced recognizers.

    Returns:
        Configured AnalyzerEngine or None if Presidio is not available
    """
    try:
        # Try to create NLP engine with fallback configuration
        try:
            nlp_configuration = {
                "nlp_engine_name": "spacy",
                "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
            }
            provider = NlpEngineProvider(nlp_configuration=nlp_configuration)
            nlp_engine = provider.create_engine()
        except Exception as e:
            print(f"Warning: Could not load spaCy model, using basic NLP engine: {e}")
            # Fallback to basic configuration
            nlp_configuration = {
                "nlp_engine_name": "spacy",
                "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
            }
            provider = NlpEngineProvider(nlp_configuration=nlp_configuration)
            nlp_engine = provider.create_engine()

        analyzer = AnalyzerEngine(nlp_engine=nlp_engine, registry=None)

        # Add enhanced recognizers with improved patterns
        enhanced_recognizers = [
            EnhancedRobustRecognizer(
                "ID",
                [
                    Pattern("ID_DASHED", r"\b\d{3}-\d{2}-\d{4}\b", 0.95),
                    Pattern("ID_SPACED", r"\b\d{3}\s\d{2}\s\d{4}\b", 0.95),
                    Pattern("ID_DOTTED", r"\b\d{3}\.\d{2}\.\d{4}\b", 0.95),
                    Pattern(
                        "ID_RAW", r"(?<!\d)\d{9}(?!\d)", 0.6
                    ),  # Avoid false positives
                ],
            ),
            EnhancedRobustRecognizer(
                "PHONE_NUMBER",
                [
                    Pattern(
                        "PHONE_FULL",
                        r"\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b",
                        0.9,
                    ),
                    Pattern(
                        "PHONE_WITH_PLUS",
                        r"\b\+\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}\b",
                        0.8,
                    ),
                    Pattern(
                        "PHONE_WITH_EXT",
                        r"\b\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\s?(?:ext|extension|x)\.?\s?\d+\b",
                        0.9,
                    ),
                ],
            ),
            EnhancedRobustRecognizer(
                "ADDRESS",
                [
                    Pattern(
                        "FULL_ADDRESS",
                        r"\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Court|Ct|Place|Pl|Way|Terrace|Ter|Circle|Cir|Parkway|Pkwy)(?:\s+(?:Apt|Apartment|Unit|Suite|Ste|#)\s*[A-Za-z0-9]+)?,\s+[A-Za-z\s]+,\s+[A-Z]{2}\s+\d{5}(?:-\d{4})?\b",
                        0.95,
                    ),
                    Pattern(
                        "STREET_ADDRESS",
                        r"\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Court|Ct|Place|Pl|Way|Terrace|Ter|Circle|Cir|Parkway|Pkwy)\b",
                        0.85,
                    ),
                    Pattern(
                        "CITY_STATE_ZIP",
                        r"\b[A-Za-z\s]+,\s+[A-Z]{2}\s+\d{5}(?:-\d{4})?\b",
                        0.9,
                    ),
                    Pattern("PO_BOX", r"\bP\.?O\.?\s+Box\s+\d+\b", 0.8),
                ],
            ),
            EnhancedRobustRecognizer(
                "EMAIL_ADDRESS",
                [
                    Pattern(
                        "EMAIL",
                        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                        0.99,
                    )
                ],
            ),
            EnhancedRobustRecognizer(
                "CREDIT_CARD",
                [
                    Pattern(
                        "CREDIT_CARD_FORMATTED",
                        r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
                        0.95,
                    ),
                    Pattern(
                        "CREDIT_CARD_AMEX",
                        r"\b3[47]\d{2}[-\s]?\d{6}[-\s]?\d{5}\b",
                        0.95,
                    ),
                    Pattern(
                        "CREDIT_CARD_RAW",
                        r"\b(?:4\d{15}|5[1-5]\d{14}|3[47]\d{13}|6(?:011|5\d{2})\d{12})\b",
                        0.9,
                    ),
                ],
            ),
            EnhancedRobustRecognizer(
                "EIN",
                [
                    Pattern("EIN_FORMATTED", r"\b\d{2}-\d{7}\b", 0.95),
                    Pattern("EIN_RAW", r"(?<!\d)\d{9}(?!\d)", 0.7),
                ],
            ),
            EnhancedRobustRecognizer(
                "ZIP",
                [
                    Pattern("ZIP_EXTENDED", r"\b\d{5}-\d{4}\b", 0.95),
                    Pattern("ZIP_BASIC", r"\b\d{5}\b", 0.85),
                ],
            ),
            EnhancedRobustRecognizer(
                "DRIVER_LICENSE", [Pattern("DL_PATTERN", r"\b[A-Z]{1,2}\d{6,8}\b", 0.8)]
            ),
            EnhancedRobustRecognizer(
                "SOCIAL_MEDIA_HANDLE",
                [
                    Pattern("TWITTER_X_HANDLE", r"@[A-Za-z0-9_]{1,15}\b", 0.9),
                    Pattern("INSTAGRAM_HANDLE", r"@[A-Za-z0-9_.]{1,30}\b", 0.9),
                    Pattern("LINKEDIN_HANDLE", r"linkedin\.com/in/[A-Za-z0-9-]+", 0.95),
                    Pattern("FACEBOOK_HANDLE", r"facebook\.com/[A-Za-z0-9.]+", 0.9),
                    Pattern("GENERIC_SOCIAL_HANDLE", r"@[A-Za-z0-9_.-]{3,30}\b", 0.7),
                ],
            ),
        ]

        for recognizer in enhanced_recognizers:
            analyzer.registry.add_recognizer(recognizer)

        return analyzer

    except Exception as e:
        print(f"Warning: Could not build Presidio analyzer: {e}")
        return None


def _chunk(text: str, size: int = 2000, overlap: int = 100) -> list[str]:
    """Split text into overlapping chunks for processing.

    Breaks large text into smaller overlapping segments to ensure PII
    entities spanning chunk boundaries are not missed.

    Parameters
    ----------
    text : str
        Text to split into chunks.
    size : int, optional
        Maximum size of each chunk in characters (default: 2000).
    overlap : int, optional
        Number of characters to overlap between chunks (default: 100).

    Returns
    -------
    List[str]
        List of text chunks with specified overlap.

    Examples
    --------
    >>> text = "A" * 3000
    >>> chunks = _chunk(text, size=1000, overlap=100)
    >>> len(chunks)
    4
    """
    if len(text) <= size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + size, len(text))
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap

        if start >= len(text):
            break

    return chunks


def hits_from_text(
    text: str, chunk_size: int = 2000, overlap: int = 100
) -> list[EntityHit]:
    """Detect PII entities in text using enhanced Presidio analyzer.

    Main entry point for PII detection. Processes text through either the
    Presidio analyzer (if available) or falls back to regex-based detection.
    Handles large texts by chunking with overlap.

    Parameters
    ----------
    text : str
        Text to analyze for PII entities.
    chunk_size : int, optional
        Maximum chunk size for processing large texts (default: 2000).
    overlap : int, optional
        Character overlap between chunks to catch boundary entities (default: 100).

    Returns
    -------
    List[EntityHit]
        List of detected PII entities with type, value, position, and context.

    Notes
    -----
    The function automatically handles:
    - Text chunking for large inputs
    - Deduplication of overlapping detections
    - Context extraction around each entity
    - Classification into Controlled/NonControlled categories
    """
    analyzer = build_analyzer()

    if analyzer:
        return _process_with_presidio(analyzer, text, chunk_size, overlap)
    else:
        return _process_with_fallback(text, chunk_size, overlap)


def _process_with_presidio(
    analyzer: AnalyzerEngine, text: str, chunk_size: int, overlap: int
) -> list[EntityHit]:
    """Process text using Presidio analyzer."""
    chunks = _chunk(text, chunk_size, overlap)
    all_hits = []

    # Initialize validator if context validation is enabled
    validator = None
    if FEATURES.get("context_validation", True):
        try:
            from .validator import ContextValidator

            validator = ContextValidator()
        except ImportError:
            pass

    for i, chunk in enumerate(chunks):
        try:
            results = analyzer.analyze(
                text=chunk,
                entities=[
                    "ID",
                    "PHONE_NUMBER",
                    "ADDRESS",
                    "EMAIL_ADDRESS",
                    "CREDIT_CARD",
                    "EIN",
                    "ZIP",
                    "DRIVER_LICENSE",
                    "SOCIAL_MEDIA_HANDLE",
                ],
                language="en",
            )

            # Adjust positions for chunk offset
            chunk_offset = i * (chunk_size - overlap)

            for result in results:
                entity_text = chunk[result.start : result.end]

                # Get context
                context_start = max(0, result.start - 30)
                context_end = min(len(chunk), result.end + 30)
                context_left = chunk[context_start : result.start].strip()
                context_right = chunk[result.end : context_end].strip()

                # Classify the entity using only chunk context (memory efficient)
                chunk_context = chunk[
                    max(0, result.start - 100) : min(len(chunk), result.end + 100)
                ]

                # Validate if validator is available
                adjusted_score = result.score
                if validator:
                    is_valid, adjusted_score = validator.validate_entity(
                        result.entity_type, entity_text, chunk_context, result.score
                    )
                    if not is_valid:
                        continue  # Skip this detection

                label = classify_label(
                    result.entity_type,
                    entity_text,
                    chunk_context,  # Use chunk context instead of full text
                    result.start,
                    result.end,
                )

                hit = EntityHit(
                    entity_type=result.entity_type,
                    value=entity_text,
                    start=chunk_offset + result.start,
                    end=chunk_offset + result.end,
                    score=adjusted_score,
                    label=label,
                    context_left=context_left,
                    context_right=context_right,
                )

                all_hits.append(hit)

            # Memory cleanup - clear chunk after processing
            del chunk
            del results

        except Exception as e:
            print(f"Error processing chunk {i}: {e}")
            continue

    return all_hits


def _process_with_fallback(text: str, chunk_size: int, overlap: int) -> list[EntityHit]:
    """Process text using fallback regex patterns."""
    from .recognizers import FALLBACK_REGEX

    all_hits = []

    for entity_type, patterns in FALLBACK_REGEX.items():
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)

            for match in matches:
                entity_text = match.group(0)

                # Get context
                context_start = max(0, match.start() - 30)
                context_end = min(len(text), match.end() + 30)
                context_left = text[context_start : match.start()].strip()
                context_right = text[match.end() : context_end].strip()

                # Classify the entity
                label = classify_label(
                    entity_type, entity_text, text, match.start(), match.end()
                )

                hit = EntityHit(
                    entity_type=entity_type,
                    value=entity_text,
                    start=match.start(),
                    end=match.end(),
                    score=0.7,  # Default confidence for regex
                    label=label,
                    context_left=context_left,
                    context_right=context_right,
                )

                all_hits.append(hit)

    return all_hits
