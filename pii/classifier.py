"""
PII Classification Logic - Simplified Controlled vs NonControlled Approach
"""

from typing import Literal, Tuple
import re

# US State abbreviations
US_STATES = [
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
]

# ZIP code pattern
ZIP_PATTERN = r'\b\d{5}(?:-\d{4})?\b'

class SimplifiedControlledDetector:
    """Simplified Controlled vs NonControlled detection with high accuracy."""
    
    def __init__(self):
        # Clear Controlled indicators
        self.controlled_indicators = {
            'phone': ['+1', '(555)', '555-', '555.', '555 '],
            'address': ['new york', 'los angeles', 'chicago', 'houston', 'phoenix', 'philadelphia', 'san antonio', 'san diego', 'dallas', 'san jose'],
            'state': US_STATES,
            'zip': ZIP_PATTERN
        }
        
        # Clear NonControlled indicators
        self.noncontrolled_indicators = {
            'phone': ['+44', '+33', '+49', '+81', '+86', '+61', '+91', '+62', '+66', '+84', '+60', '+63'],
            'address': ['london', 'manchester', 'toronto', 'montreal', 'vancouver', 'sydney', 'melbourne', 'berlin', 'munich', 'paris', 'lyon', 'tokyo', 'osaka', 'beijing', 'shanghai'],
            'postal_codes': {
                'uk': r'\b[A-Z]{1,2}\d{1,2}\s+\d[A-Z]{2}\b',
                'canada': r'\b[A-Z]\d[A-Z]\s+\d[A-Z]\d\b',
                'australia': r'\b[A-Z]{2,3}\s+\d{4}\b'
            },
            'domains': ['.uk', '.ca', '.au', '.de', '.fr', '.jp', '.cn', '.in', '.sg', '.my', '.th', '.vn', '.ph']
        }

    def classify_entity(self, entity_type: str, value: str, context: str) -> Tuple[str, float]:
        """Classify entity using simplified Controlled vs NonControlled approach."""
        if entity_type == "ID":
            return "Controlled", 0.95  # ID numbers are always Controlled
        elif entity_type == "DRIVER_LICENSE":
            return "Controlled", 0.9   # Driver licenses are Controlled jurisdiction
        elif entity_type == "EIN":
            return "Controlled", 0.95  # EIN is always Controlled
        elif entity_type == "ZIP":
            return "Controlled", 0.9   # ZIP codes are Controlled
        elif entity_type == "CREDIT_CARD":
            return "NonControlled", 0.8  # Credit cards are global
        
        value_lower = value.lower()
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

    def _classify_phone(self, phone: str, context: str) -> Tuple[str, float]:
        # Smart phone classification based on patterns, not hardcoded lists
        
        # Controlled format: +1 or starts with 1, followed by 10 digits
        if re.search(r'^\+?1[\s\-\.]?\(?[2-9]\d{2}\)?[\s\-\.]?\d{3}[\s\-\.]?\d{4}$', phone):
            return "Controlled", 0.95
        
        # International format: +XX (any non-1 country code)
        if re.search(r'^\+(?!1\b)\d{1,4}[\s\-\.]?\d', phone):
            return "NonControlled", 0.9
        
        # Clean digits only analysis
        cleaned = re.sub(r'[^\d]', '', phone)
        
        # 10 digits starting with valid area code = likely Controlled
        if len(cleaned) == 10 and cleaned[0] in '23456789':
            return "Controlled", 0.8
        
        # 11 digits starting with 1 = Controlled with country code
        if len(cleaned) == 11 and cleaned.startswith('1'):
            return "Controlled", 0.85
        
        # More than 11 digits = likely international
        if len(cleaned) > 11:
            return "NonControlled", 0.75
        
        # Less than 10 digits = incomplete/invalid
        if len(cleaned) < 10:
            return "NonControlled", 0.6
        
        # Default fallback
        return "Controlled", 0.5

    def _classify_address(self, address: str, context: str) -> Tuple[str, float]:
        # Smart address classification using pattern recognition
        
        # Definitive Controlled indicators: State abbreviations with ZIP
        if re.search(r'\b[A-Z]{2}\s+\d{5}(?:-\d{4})?\b', address):
            return "Controlled", 0.95
        
        # Definitive international postal formats
        patterns = [
            (r'\b[A-Z]{1,2}\d{1,2}[A-Z]?\s+\d[A-Z]{2}\b', 0.95),  # UK: SW1A 2AA
            (r'\b[A-Z]\d[A-Z]\s+\d[A-Z]\d\b', 0.95),              # Canada: K1A 0A6
            (r'\b\d{4}\s*[A-Z]{2}\b', 0.9),                        # Netherlands: 1000 AB
            (r'\b\d{5}\s+[A-Z][a-z]{2,}\b', 0.85),                # Europe: 75001 Paris
        ]
        
        for pattern, confidence in patterns:
            if re.search(pattern, address):
                return "NonControlled", confidence
        
        # Smart linguistic analysis - non-English address components
        non_english_patterns = [
            r'\b(?:rue|via|straße|strasse|avenida|boulevard)\b',   # Street types
            r'\b(?:platz|gatan|vägen|corso|rua|calle)\b',          # More street types
            r'\b(?:postbus|boîte|casella)\b',                      # PO Box equivalents
        ]
        
        for pattern in non_english_patterns:
            if re.search(pattern, address, re.IGNORECASE):
                return "NonControlled", 0.8
        
        # Check for obvious country/region indicators
        if re.search(r'\b(?:uk|united kingdom|canada|australia|germany|france|italy|spain|netherlands|sweden|norway|denmark|finland|belgium|austria|switzerland)\b', address, re.IGNORECASE):
            return "NonControlled", 0.85
        
        # Controlled-style address format: Number + Street + City, State ZIP
        controlled_format = r'\b\d+\s+[A-Za-z\s]+(?:street|st|avenue|ave|road|rd|drive|dr|lane|ln|boulevard|blvd|way|court|ct|place|pl)\b'
        if re.search(controlled_format, address, re.IGNORECASE):
            return "Controlled", 0.75
        
        # Just a ZIP code alone (5 or 5+4 digits)
        if re.search(r'^\d{5}(?:-\d{4})?$', address.strip()):
            return "Controlled", 0.9
        
        # Default: if no clear indicators, lean towards Controlled for domestic systems
        return "Controlled", 0.5

    def _classify_email(self, email: str, context: str) -> Tuple[str, float]:
        # Smart email classification using pattern recognition
        
        # Controlled government/official domains (high confidence Controlled)
        if re.search(r'\.(?:gov|mil|edu)$', email, re.IGNORECASE):
            return "Controlled", 0.95
        
        # Country-specific TLDs (two-letter country codes)
        if re.search(r'\.(?!com|org|net|info|biz)[a-z]{2}$', email, re.IGNORECASE):
            return "NonControlled", 0.9
        
        # Generic TLDs - analyze context
        if re.search(r'\.(?:com|org|net|info|biz)$', email, re.IGNORECASE):
            # Check context for international indicators
            intl_context = re.search(r'\b(?:international|global|worldwide|europe|asia|foreign|overseas|uk|canada|australia)\b', context, re.IGNORECASE)
            if intl_context:
                return "NonControlled", 0.7
            # Default to Controlled for generic domains in domestic-focused context
            return "Controlled", 0.65
        
        # Unknown/new TLDs - lean international
        return "NonControlled", 0.6

    def _classify_social_media(self, handle: str, context: str) -> Tuple[str, float]:
        # Smart social media handle classification
        
        # Check for platform-specific URLs with geographic indicators
        if re.search(r'linkedin\.com/in/.+', handle, re.IGNORECASE):
            # LinkedIn profiles - check for international indicators in context
            if re.search(r'\b(?:uk|canada|australia|europe|asia|international|global)\b', context, re.IGNORECASE):
                return "NonControlled", 0.8
            return "Controlled", 0.7
        
        if re.search(r'facebook\.com/.+', handle, re.IGNORECASE):
            # Facebook profiles - check context for geographic clues
            if re.search(r'\b(?:uk|canada|australia|europe|asia|international|global)\b', context, re.IGNORECASE):
                return "NonControlled", 0.75
            return "Controlled", 0.65
        
        # Simple @ handles - analyze context
        if handle.startswith('@'):
            # Check context for international language/content
            intl_patterns = [
                r'\b(?:international|global|worldwide|europe|asia|foreign|overseas)\b',
                r'\b(?:uk|canada|australia|germany|france|italy|spain|netherlands)\b',
                r'[\u00C0-\u017F]',  # Accented characters
                r'[\u0400-\u04FF]',  # Cyrillic
                r'[\u4E00-\u9FFF]',  # Chinese
            ]
            
            for pattern in intl_patterns:
                if re.search(pattern, context, re.IGNORECASE):
                    return "NonControlled", 0.7
            
            # Default to Controlled for @ handles in domestic context
            return "Controlled", 0.6
        
        # Default classification for social media handles
        return "NonControlled", 0.5

# Global detector instance
_controlled_detector = SimplifiedControlledDetector()

def classify_label(entity_type: str, raw_value: str, full_text: str, start: int, end: int) -> Literal["Controlled", "NonControlled"]:
    """
    Classify PII entity as Controlled or NonControlled.
    
    Args:
        entity_type: Type of PII entity
        raw_value: Raw detected value
        full_text: Full text content
        start: Start position of entity
        end: End position of entity
    
    Returns:
        "Controlled" for controlled jurisdiction entities, "NonControlled" for non-controlled entities
    """
    # Get context around the entity
    context_start = max(0, start - 100)
    context_end = min(len(full_text), end + 100)
    context = full_text[context_start:context_end]
    
    # Use simplified Controlled detector
    classification, _ = _controlled_detector.classify_entity(entity_type, raw_value, context)
    return classification

def validate_luhn(number: str) -> bool:
    """Validate credit card number using Luhn algorithm."""
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
    """Validate bank routing number using ABA checksum."""
    if not routing.isdigit() or len(routing) != 9:
        return False
    
    digits = [int(d) for d in routing]
    weights = [3, 7, 1, 3, 7, 1, 3, 7, 1]
    
    checksum = sum(d * w for d, w in zip(digits, weights))
    return checksum % 10 == 0 