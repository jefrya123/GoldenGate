"""PII Classification Logic - Simplified Controlled vs NonControlled Approach.

This module provides intelligent classification of PII entities into Controlled
and NonControlled categories using
pattern recognition, linguistic analysis, and contextual clues.
"""

import re
from typing import Literal

# US State abbreviations
US_STATES = [
    "AL",
    "AK",
    "AZ",
    "AR",
    "CA",
    "CO",
    "CT",
    "DE",
    "FL",
    "GA",
    "HI",
    "ID",
    "IL",
    "IN",
    "IA",
    "KS",
    "KY",
    "LA",
    "ME",
    "MD",
    "MA",
    "MI",
    "MN",
    "MS",
    "MO",
    "MT",
    "NE",
    "NV",
    "NH",
    "NJ",
    "NM",
    "NY",
    "NC",
    "ND",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VT",
    "VA",
    "WA",
    "WV",
    "WI",
    "WY",
]

# ZIP code pattern
ZIP_PATTERN = r"\b\d{5}(?:-\d{4})?\b"


class SimplifiedControlledDetector:
    """Simplified Controlled vs NonControlled detection with high accuracy.

    Uses pattern matching and linguistic analysis to classify PII entities
    based on jurisdiction. Controlled entities are typically US-based,
    while NonControlled entities follow different patterns.

    Attributes
    ----------
    controlled_indicators : dict
        Patterns and keywords indicating Controlled entities.
    noncontrolled_indicators : dict
        Patterns and keywords indicating NonControlled entities.
    """

    def __init__(self):
        # Clear Controlled indicators
        self.controlled_indicators = {
            "phone": ["+1", "(555)", "555-", "555.", "555 "],
            "address": [
                "new york",
                "los angeles",
                "chicago",
                "houston",
                "phoenix",
                "philadelphia",
                "san antonio",
                "san diego",
                "dallas",
                "san jose",
            ],
            "state": US_STATES,
            "zip": ZIP_PATTERN,
        }

        # Clear NonControlled indicators
        self.noncontrolled_indicators = {
            "phone": [
                "+44",
                "+33",
                "+49",
                "+81",
                "+86",
                "+61",
                "+91",
                "+62",
                "+66",
                "+84",
                "+60",
                "+63",
            ],
            "address": [
                "london",
                "manchester",
                "toronto",
                "montreal",
                "vancouver",
                "sydney",
                "melbourne",
                "berlin",
                "munich",
                "paris",
                "lyon",
                "tokyo",
                "osaka",
                "beijing",
                "shanghai",
            ],
            "postal_codes": {
                "uk": r"\b[A-Z]{1,2}\d{1,2}\s+\d[A-Z]{2}\b",
                "canada": r"\b[A-Z]\d[A-Z]\s+\d[A-Z]\d\b",
                "australia": r"\b[A-Z]{2,3}\s+\d{4}\b",
            },
            "domains": [
                ".uk",
                ".ca",
                ".au",
                ".de",
                ".fr",
                ".jp",
                ".cn",
                ".in",
                ".sg",
                ".my",
                ".th",
                ".vn",
                ".ph",
            ],
        }

    def classify_entity(
        self, entity_type: str, value: str, context: str
    ) -> tuple[str, float]:
        """Classify entity using simplified Controlled vs NonControlled approach.

        Parameters
        ----------
        entity_type : str
            Type of PII entity (ID, PHONE_NUMBER, ADDRESS, etc.).
        value : str
            The detected entity value.
        context : str
            Surrounding text context for analysis.

        Returns
        -------
        tuple[str, float]
            A tuple containing:
            - classification (str): "Controlled" or "NonControlled"
            - confidence (float): Confidence score between 0 and 1
        """
        if entity_type == "ID":
            return "Controlled", 0.95  # ID numbers are always Controlled
        elif entity_type == "DRIVER_LICENSE":
            return "Controlled", 0.9  # Driver licenses are Controlled jurisdiction
        elif entity_type == "EIN":
            return "Controlled", 0.95  # EIN is always Controlled
        elif entity_type == "ZIP":
            return "Controlled", 0.9  # ZIP codes are Controlled
        elif entity_type == "CREDIT_CARD":
            return "NonControlled", 0.8  # Credit cards are global

        context_lower = context.lower()

        if entity_type == "PHONE_NUMBER":
            return self._classify_phone(value, context_lower)
        elif entity_type == "ADDRESS":
            return self._classify_address(value, context_lower)
        elif entity_type == "EMAIL_ADDRESS":
            return self._classify_email(value, context_lower)
        elif entity_type == "SOCIAL_MEDIA_HANDLE":
            return self._classify_social_media(value, context_lower)
        else:
            return "NonControlled", 0.5

    def _classify_phone(self, phone: str, context: str) -> tuple[str, float]:
        """Classify phone numbers using smart pattern recognition.

        Parameters
        ----------
        phone : str
            Phone number to classify.
        context : str
            Surrounding text context.

        Returns
        -------
        tuple[str, float]
            Classification and confidence score.
        """

        # Controlled format: +1 or starts with 1, followed by 10 digits
        if re.search(
            r"^\+?1[\s\-\.]?\(?[2-9]\d{2}\)?[\s\-\.]?\d{3}[\s\-\.]?\d{4}$", phone
        ):
            return "Controlled", 0.95

        # Format with plus code: +XX (any non-1 country code)
        if re.search(r"^\+(?!1\b)\d{1,4}[\s\-\.]?\d", phone):
            return "NonControlled", 0.9

        # Clean digits only analysis
        cleaned = re.sub(r"[^\d]", "", phone)

        # 10 digits starting with valid area code = likely Controlled
        if len(cleaned) == 10 and cleaned[0] in "23456789":
            return "Controlled", 0.8

        # 11 digits starting with 1 = Controlled with country code
        if len(cleaned) == 11 and cleaned.startswith("1"):
            return "Controlled", 0.85

        # More than 11 digits = likely NonControlled
        if len(cleaned) > 11:
            return "NonControlled", 0.75

        # Less than 10 digits = incomplete/invalid
        if len(cleaned) < 10:
            return "NonControlled", 0.6

        # Default fallback
        return "Controlled", 0.5

    def _classify_address(self, address: str, context: str) -> tuple[str, float]:
        """Classify addresses using pattern recognition and linguistic analysis.

        Parameters
        ----------
        address : str
            Address text to classify.
        context : str
            Surrounding text context.

        Returns
        -------
        tuple[str, float]
            Classification and confidence score.
        """

        # Definitive Controlled indicators: State abbreviations with ZIP
        if re.search(r"\b[A-Z]{2}\s+\d{5}(?:-\d{4})?\b", address):
            return "Controlled", 0.95

        # Definitive NonControlled postal formats
        patterns = [
            (r"\b[A-Z]{1,2}\d{1,2}[A-Z]?\s+\d[A-Z]{2}\b", 0.95),  # UK: SW1A 2AA
            (r"\b[A-Z]\d[A-Z]\s+\d[A-Z]\d\b", 0.95),  # Canada: K1A 0A6
            (r"\b\d{4}\s*[A-Z]{2}\b", 0.9),  # Netherlands: 1000 AB
            (r"\b\d{5}\s+[A-Z][a-z]{2,}\b", 0.85),  # Europe: 75001 Paris
        ]

        for pattern, confidence in patterns:
            if re.search(pattern, address):
                return "NonControlled", confidence

        # Smart linguistic analysis - non-English address components
        non_english_patterns = [
            r"\b(?:rue|via|straße|strasse|avenida|boulevard)\b",  # Street types
            r"\b(?:platz|gatan|vägen|corso|rua|calle)\b",  # More street types
            r"\b(?:postbus|boîte|casella)\b",  # PO Box equivalents
        ]

        for pattern in non_english_patterns:
            if re.search(pattern, address, re.IGNORECASE):
                return "NonControlled", 0.8

        # Check for obvious country/region indicators
        if re.search(
            r"\b(?:uk|united kingdom|canada|australia|germany|france|italy|spain|netherlands|sweden|norway|denmark|finland|belgium|austria|switzerland)\b",
            address,
            re.IGNORECASE,
        ):
            return "NonControlled", 0.85

        # Controlled-style address format: Number + Street + City, State ZIP
        controlled_format = r"\b\d+\s+[A-Za-z\s]+(?:street|st|avenue|ave|road|rd|drive|dr|lane|ln|boulevard|blvd|way|court|ct|place|pl)\b"
        if re.search(controlled_format, address, re.IGNORECASE):
            return "Controlled", 0.75

        # Just a ZIP code alone (5 or 5+4 digits)
        if re.search(r"^\d{5}(?:-\d{4})?$", address.strip()):
            return "Controlled", 0.9

        # Default: if no clear indicators, lean towards Controlled
        return "Controlled", 0.5

    def _classify_email(self, email: str, context: str) -> tuple[str, float]:
        """Classify email addresses using domain analysis.

        Parameters
        ----------
        email : str
            Email address to classify.
        context : str
            Surrounding text context.

        Returns
        -------
        tuple[str, float]
            Classification and confidence score.
        """

        # Controlled government/official domains (high confidence Controlled)
        if re.search(r"\.(?:gov|mil|edu)$", email, re.IGNORECASE):
            return "Controlled", 0.95

        # Country-specific TLDs (two-letter country codes)
        if re.search(r"\.(?!com|org|net|info|biz)[a-z]{2}$", email, re.IGNORECASE):
            return "NonControlled", 0.9

        # Generic TLDs - analyze context
        if re.search(r"\.(?:com|org|net|info|biz)$", email, re.IGNORECASE):
            # Check context for NonControlled indicators
            intl_context = re.search(
                r"\b(?:global|worldwide|europe|asia|overseas|uk|canada|australia)\b",
                context,
                re.IGNORECASE,
            )
            if intl_context:
                return "NonControlled", 0.7
            # Default to Controlled for generic domains
            return "Controlled", 0.65

        # Unknown/new TLDs - lean NonControlled
        return "NonControlled", 0.6

    def _classify_social_media(self, handle: str, context: str) -> tuple[str, float]:
        """Classify social media handles using platform and context analysis.

        Parameters
        ----------
        handle : str
            Social media handle or URL.
        context : str
            Surrounding text context.

        Returns
        -------
        tuple[str, float]
            Classification and confidence score.
        """

        # Check for platform-specific URLs with geographic indicators
        if re.search(r"linkedin\.com/in/.+", handle, re.IGNORECASE):
            # LinkedIn profiles - check for international indicators in context
            if re.search(
                r"\b(?:uk|canada|australia|europe|asia|global)\b",
                context,
                re.IGNORECASE,
            ):
                return "NonControlled", 0.8
            return "Controlled", 0.7

        if re.search(r"facebook\.com/.+", handle, re.IGNORECASE):
            # Facebook profiles - check context for geographic clues
            if re.search(
                r"\b(?:uk|canada|australia|europe|asia|global)\b",
                context,
                re.IGNORECASE,
            ):
                return "NonControlled", 0.75
            return "Controlled", 0.65

        # Simple @ handles - analyze context
        if handle.startswith("@"):
            # Check context for NonControlled language/content
            intl_patterns = [
                r"\b(?:global|worldwide|europe|asia|overseas)\b",
                r"\b(?:uk|canada|australia|germany|france|italy|spain|netherlands)\b",
                r"[\u00C0-\u017F]",  # Accented characters
                r"[\u0400-\u04FF]",  # Cyrillic
                r"[\u4E00-\u9FFF]",  # Chinese
            ]

            for pattern in intl_patterns:
                if re.search(pattern, context, re.IGNORECASE):
                    return "NonControlled", 0.7

            # Default to Controlled for @ handles
            return "Controlled", 0.6

        # Default classification for social media handles
        return "NonControlled", 0.5


# Global detector instance
_controlled_detector = SimplifiedControlledDetector()


def classify_label(
    entity_type: str, raw_value: str, full_text: str, start: int, end: int
) -> Literal["Controlled", "NonControlled"]:
    """Classify PII entity as Controlled or NonControlled.

    Main entry point for entity classification that extracts context
    and delegates to the specialized classifier.

    Parameters
    ----------
    entity_type : str
        Type of PII entity (ID, PHONE_NUMBER, etc.).
    raw_value : str
        Raw detected value.
    full_text : str
        Full text content for context extraction.
    start : int
        Start position of entity in text.
    end : int
        End position of entity in text.

    Returns
    -------
    Literal["Controlled", "NonControlled"]
        "Controlled" for certain patterns, "NonControlled" for others.

    Examples
    --------
    >>> classify_label("PHONE_NUMBER", "555-123-4567", "Call us at 555-123-4567", 11, 23)
    'Controlled'
    """
    # Get context around the entity
    context_start = max(0, start - 100)
    context_end = min(len(full_text), end + 100)
    context = full_text[context_start:context_end]

    # Use simplified Controlled detector
    classification, _ = _controlled_detector.classify_entity(
        entity_type, raw_value, context
    )
    return classification


def validate_luhn(number: str) -> bool:
    """Validate credit card number using Luhn algorithm.

    Parameters
    ----------
    number : str
        Credit card number (digits only or with formatting).

    Returns
    -------
    bool
        True if valid according to Luhn algorithm, False otherwise.

    Notes
    -----
    The Luhn algorithm (mod-10 checksum) is used by all major
    credit card companies to validate card numbers.
    """
    digits = [int(d) for d in str(number) if d.isdigit()]
    if len(digits) < 13 or len(digits) > 19:
        return False

    checksum = 0
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]

    checksum += sum(odd_digits)
    for d in even_digits:
        checksum += sum(divmod(d * 2, 10))

    return checksum % 10 == 0


def validate_aba_routing(routing: str) -> bool:
    """Validate bank routing number using ABA checksum.

    Parameters
    ----------
    routing : str
        9-digit bank routing number.

    Returns
    -------
    bool
        True if valid ABA routing number, False otherwise.

    Notes
    -----
    Uses the ABA (American Bankers Association) checksum algorithm
    with weights [3, 7, 1, 3, 7, 1, 3, 7, 1].
    """
    if not routing.isdigit() or len(routing) != 9:
        return False

    digits = [int(d) for d in routing]
    weights = [3, 7, 1, 3, 7, 1, 3, 7, 1]

    checksum = sum(d * w for d, w in zip(digits, weights, strict=False))
    return checksum % 10 == 0
