"""
PII Classification Logic - Simplified US vs Foreign Approach
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
            return "Controlled", 0.95  # SSN is always Controlled
        
        value_lower = value.lower()
        context_lower = context.lower()
        
        if entity_type == "PHONE_NUMBER":
            return self._classify_phone(value, context_lower)
        elif entity_type == "ADDRESS":
            return self._classify_address(value, context_lower)
        elif entity_type == "EMAIL_ADDRESS":
            return self._classify_email(value, context_lower)
        else:
            return "NonControlled", 0.5

    def _classify_phone(self, phone: str, context: str) -> Tuple[str, float]:
        # Clear Controlled indicators
        for indicator in self.controlled_indicators['phone']:
            if indicator in phone:
                return "Controlled", 0.9
        
        # Clear NonControlled indicators
        for indicator in self.noncontrolled_indicators['phone']:
            if indicator in phone:
                return "NonControlled", 0.9
        
        # Check if it's a 10-digit Controlled number
        cleaned = re.sub(r'[^\d]', '', phone)
        if len(cleaned) == 10 or (len(cleaned) == 11 and cleaned.startswith('1')):
            return "Controlled", 0.8
        
        # Default to Controlled (more common in Controlled-based systems)
        return "Controlled", 0.6

    def _classify_address(self, address: str, context: str) -> Tuple[str, float]:
        address_lower = address.lower()
        
        # Clear Controlled indicators
        for city in self.controlled_indicators['address']:
            if city in address_lower:
                return "Controlled", 0.9
        
        for state in self.controlled_indicators['state']:
            if f', {state}' in address or f', {state} ' in address:
                return "Controlled", 0.9
        
        if re.search(self.controlled_indicators['zip'], address):
            return "Controlled", 0.9
        
        # Clear NonControlled indicators
        for city in self.noncontrolled_indicators['address']:
            if city in address_lower:
                return "NonControlled", 0.9
        
        for country, pattern in self.noncontrolled_indicators['postal_codes'].items():
            if re.search(pattern, address):
                return "NonControlled", 0.9
        
        # Default to Controlled (more common in Controlled-based systems)
        return "Controlled", 0.6

    def _classify_email(self, email: str, context: str) -> Tuple[str, float]:
        email_lower = email.lower()
        
        # Clear NonControlled indicators
        for domain in self.noncontrolled_indicators['domains']:
            if domain in email_lower:
                return "NonControlled", 0.9
        
        # Default to NonControlled for emails (global nature)
        return "NonControlled", 0.6

# Global detector instance
_controlled_detector = SimplifiedControlledDetector()

def classify_label(entity_type: str, raw_value: str, full_text: str, start: int, end: int) -> Literal["Controlled", "NonControlled"]:
    """
    Classify PII entity as Controlled (US) or NonControlled (Foreign).
    
    Args:
        entity_type: Type of PII entity
        raw_value: Raw detected value
        full_text: Full text content
        start: Start position of entity
        end: End position of entity
    
    Returns:
        "Controlled" for US entities, "NonControlled" for foreign entities
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
    """Validate Controlled bank routing number using ABA checksum."""
    if not routing.isdigit() or len(routing) != 9:
        return False
    
    digits = [int(d) for d in routing]
    weights = [3, 7, 1, 3, 7, 1, 3, 7, 1]
    
    checksum = sum(d * w for d, w in zip(digits, weights))
    return checksum % 10 == 0 