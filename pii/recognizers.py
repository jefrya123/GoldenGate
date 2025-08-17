"""
Custom PII recognizers for Presidio and fallback regex patterns.
"""

import re
from typing import Dict, List, Optional, Pattern
from presidio_analyzer import Pattern, PatternRecognizer, RecognizerResult
from presidio_analyzer.nlp_engine import NlpArtifacts


# Fallback regex patterns for when Presidio is not available
FALLBACK_REGEX = {
    'ID': [
        # ID pattern (XXX-XX-XXXX)
        r'\b\d{3}-\d{2}-\d{4}\b',
        # ID with spaces (XXX XX XXXX)
        r'\b\d{3}\s\d{2}\s\d{4}\b',
        # ID without dashes
        r'\b\d{9}\b'
    ],
    'EIN': [
        # EIN pattern (XX-XXXXXXX)
        r'\b\d{2}-\d{7}\b',
        # EIN without dashes
        r'\b\d{9}\b'
    ],
    'ZIP': [
        # ZIP code (5 digits or 5+4 format)
        r'\b\d{5}(?:-\d{4})?\b'
    ],
    'EMAIL_ADDRESS': [
        # Standard email pattern
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    ],
    'CREDIT_CARD': [
        # Credit card with various separators (13-19 digits)
        r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{1,4}\b',
        # Credit card without separators
        r'\b\d{13,19}\b'
    ],
    'PHONE_NUMBER': [
        # US phone numbers with various formats
        r'\b\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
        # International format
        r'\b\+\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}\b'
    ],
    'SOCIAL_MEDIA_HANDLE': [
        # LinkedIn profiles
        r'\b(?:https?://)?(?:www\.)?linkedin\.com/in/[A-Za-z0-9-]+\b',
        # Facebook profiles
        r'\b(?:https?://)?(?:www\.)?facebook\.com/[A-Za-z0-9.]+\b',
        # Generic social handles (standalone @username)
        r'@[A-Za-z0-9_]{1,30}\b'
    ],
    'BANK_ROUTING': [
        # 9-digit routing numbers
        r'\b\d{9}\b'
    ],
    'DRIVER_LICENSE': [
        # California: 1 letter + 7 digits
        r'\b[A-Z]\d{7}\b',
        # Texas: 8 digits
        r'\b\d{8}\b',
        # New York: 9 digits
        r'\b\d{9}\b'
    ]
}


class CustomIDRecognizer(PatternRecognizer):
    """Custom recognizer for ID numbers."""
    
    def __init__(self):
        patterns = [
            Pattern("ID", r'\b\d{3}-\d{2}-\d{4}\b', 0.9),
            Pattern("ID_NO_DASHES", r'\b\d{9}\b', 0.8)
        ]
        super().__init__(
            supported_entity="ID",
            patterns=patterns,
            supported_language="en"
        )


class CustomEINRecognizer(PatternRecognizer):
    """Custom recognizer for Employer Identification Numbers."""
    
    def __init__(self):
        patterns = [
            Pattern("EIN", r'\b\d{2}-\d{7}\b', 0.9),
            Pattern("EIN_NO_DASHES", r'\b\d{9}\b', 0.8)
        ]
        super().__init__(
            supported_entity="EIN",
            patterns=patterns,
            supported_language="en"
        )


class CustomZIPRecognizer(PatternRecognizer):
    """Custom recognizer for ZIP codes."""
    
    def __init__(self):
        patterns = [
            Pattern("ZIP", r'\b\d{5}(?:-\d{4})?\b', 0.9)
        ]
        super().__init__(
            supported_entity="ZIP",
            patterns=patterns,
            supported_language="en"
        )


class CustomBankRoutingRecognizer(PatternRecognizer):
    """Custom recognizer for bank routing numbers."""
    
    def __init__(self):
        patterns = [
            Pattern("BANK_ROUTING", r'\b\d{9}\b', 0.8)
        ]
        super().__init__(
            supported_entity="BANK_ROUTING",
            patterns=patterns,
            supported_language="en"
        )


class CustomDriverLicenseRecognizer(PatternRecognizer):
    """Custom recognizer for driver license numbers."""
    
    def __init__(self):
        patterns = [
            Pattern("CA_LICENSE", r'\b[A-Z]\d{7}\b', 0.9),  # California
            Pattern("TX_LICENSE", r'\b\d{8}\b', 0.8),       # Texas
            Pattern("NY_LICENSE", r'\b\d{9}\b', 0.8)        # New York
        ]
        super().__init__(
            supported_entity="DRIVER_LICENSE",
            patterns=patterns,
            supported_language="en"
        )


class CustomSocialMediaHandleRecognizer(PatternRecognizer):
    """Custom recognizer for social media handles and profiles."""
    
    def __init__(self):
        patterns = [
            Pattern("LINKEDIN_PROFILE", r'\b(?:https?://)?(?:www\.)?linkedin\.com/in/[A-Za-z0-9-]+\b', 0.9),
            Pattern("FACEBOOK_PROFILE", r'\b(?:https?://)?(?:www\.)?facebook\.com/[A-Za-z0-9.]+\b', 0.9),
            Pattern("GENERIC_HANDLE", r'@[A-Za-z0-9_]{1,30}\b', 0.9)
        ]
        super().__init__(
            supported_entity="SOCIAL_MEDIA_HANDLE",
            patterns=patterns,
            supported_language="en"
        )


def get_custom_recognizers() -> List[PatternRecognizer]:
    """
    Get list of custom recognizers for Presidio integration.
    
    Returns:
        List of custom PatternRecognizer instances
    """
    return [
        CustomIDRecognizer(),
        CustomEINRecognizer(),
        CustomZIPRecognizer(),
        CustomBankRoutingRecognizer(),
        CustomDriverLicenseRecognizer(),
        CustomSocialMediaHandleRecognizer()
    ]


def apply_fallback_regex(text: str) -> List[Dict]:
    """
    Apply fallback regex patterns when Presidio is not available.
    
    Args:
        text: Text to analyze
        
    Returns:
        List of dictionaries with detection results
    """
    results = []
    
    for entity_type, patterns in FALLBACK_REGEX.items():
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                results.append({
                    'entity_type': entity_type,
                    'value': match.group(),
                    'start': match.start(),
                    'end': match.end(),
                    'score': 0.8  # Default confidence score
                })
    
    return results 