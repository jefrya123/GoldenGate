"""Context validation for reducing false positives in PII detection.

This module provides advanced validation logic to reduce false positives
in PII detection by analyzing surrounding context, checking against known
patterns, and applying confidence adjustments based on contextual clues.
"""

import re

from config import (
    CONTEXT_BOOST,
    CONTEXT_KEYWORDS,
    FALSE_POSITIVE_INDICATORS,
    FALSE_POSITIVE_PENALTY,
    INVALID_AREA_CODES,
    INVALID_ID_PATTERNS,
    MIN_CONFIDENCE,
)


class ContextValidator:
    """Validates PII detections using context and patterns.

    This validator applies sophisticated rules to filter out false positives
    in PII detection. It uses context analysis, pattern matching, and
    algorithmic validation (like Luhn check for credit cards) to ensure
    high-quality detection results.

    Attributes
    ----------
    context_pattern : re.Pattern
        Compiled regex for matching positive context keywords.
    false_positive_pattern : re.Pattern
        Compiled regex for matching false positive indicators.
    """

    def __init__(self):
        """Initialize validator with compiled patterns.

        Pre-compiles regex patterns for efficient repeated use during
        validation operations.
        """
        # Compile regex patterns for efficiency
        self.context_pattern = re.compile(
            r"\b(" + "|".join(re.escape(kw) for kw in CONTEXT_KEYWORDS) + r")\b",
            re.IGNORECASE,
        )
        self.false_positive_pattern = re.compile(
            r"\b("
            + "|".join(re.escape(fp) for fp in FALSE_POSITIVE_INDICATORS)
            + r")\b",
            re.IGNORECASE,
        )

    def validate_id(self, value: str, context: str = "") -> tuple[bool, float]:
        """Validate ID with context.

        Performs comprehensive validation of identification numbers including
        format checking, invalid pattern detection, and contextual analysis.

        Parameters
        ----------
        value : str
            The ID value detected (can be formatted with dashes, spaces, or dots).
        context : str, optional
            Surrounding text context for validation (default: empty string).

        Returns
        -------
        tuple[bool, float]
            A tuple containing:
            - is_valid (bool): Whether the ID passes validation
            - confidence_adjustment (float): Score adjustment based on context

        Notes
        -----
        Validation includes:
        - Checking against known invalid ID patterns
        - Verifying area codes are in valid ranges
        - Detecting version numbers that may be false positives
        """
        # Normalize ID
        normalized = value.replace("-", "").replace(" ", "").replace(".", "")

        # Check invalid patterns
        if value in INVALID_ID_PATTERNS:
            return False, 0.0

        # Check for all same digits
        if len(set(normalized)) == 1:
            return False, 0.0

        # Check invalid ranges
        if normalized.startswith("000") or normalized.startswith("666"):
            return False, 0.0

        # Check area number (first 3 digits)
        area = normalized[:3]
        if area == "000" or int(area) > 899:
            return False, 0.0

        # Context validation
        confidence_adj = self._check_context(context)

        # Check for version number patterns
        if re.search(r"version|v\d+\.\d+\.\d+", context, re.IGNORECASE):
            confidence_adj -= 0.5

        return True, confidence_adj

    def validate_phone(self, value: str, context: str = "") -> tuple[bool, float]:
        """Validate phone number with context.

        Validates phone numbers by checking area codes, detecting timestamp
        false positives, and analyzing surrounding context.

        Parameters
        ----------
        value : str
            The phone number detected (various formats supported).
        context : str, optional
            Surrounding text context for validation (default: empty string).

        Returns
        -------
        tuple[bool, float]
            A tuple containing:
            - is_valid (bool): Whether the phone number passes validation
            - confidence_adjustment (float): Score adjustment based on context

        Notes
        -----
        Special handling for:
        - Invalid area codes (000, 001, etc.)
        - 555 numbers (only 555-0100 through 555-0199 are valid)
        - Timestamp false positives (Unix epoch times)
        """
        # Extract area code for US phones
        us_phone_match = re.match(r"\(?(\d{3})\)?[-.\s]?\d{3}[-.\s]?\d{4}", value)
        if us_phone_match:
            area_code = us_phone_match.group(1)
            if area_code in INVALID_AREA_CODES:
                # Exception for 555 numbers used in examples
                if area_code == "555":
                    # 555-0100 through 555-0199 are valid
                    rest = (
                        value.replace(area_code, "").replace("-", "").replace(" ", "")
                    )
                    if not (100 <= int(rest[:4]) <= 199):
                        return False, 0.0
                else:
                    return False, 0.0

        # Context validation
        confidence_adj = self._check_context(context)

        # Check for timestamp patterns (false positive)
        if re.search(r"timestamp|unix|epoch|\d{10,13}", context, re.IGNORECASE):
            confidence_adj -= 0.4

        return True, confidence_adj

    def validate_credit_card(self, value: str, context: str = "") -> tuple[bool, float]:
        """
        Validate credit card with Luhn algorithm and context.

        Args:
            value: The credit card number detected
            context: Surrounding text context

        Returns:
            (is_valid, confidence_adjustment)
        """
        # Remove non-digits
        digits = re.sub(r"\D", "", value)

        # Luhn algorithm
        if not self._luhn_check(digits):
            return False, 0.0

        # Check for test card numbers
        if digits in {"4111111111111111", "5555555555554444", "378282246310005"}:
            return False, 0.0

        # Context validation
        confidence_adj = self._check_context(context)

        return True, confidence_adj

    def validate_email(self, value: str, context: str = "") -> tuple[bool, float]:
        """
        Validate email address with context.

        Args:
            value: The email address detected
            context: Surrounding text context

        Returns:
            (is_valid, confidence_adjustment)
        """
        # Check for obvious test/example emails
        lower_email = value.lower()
        if any(
            test in lower_email
            for test in [
                "example.com",
                "test.com",
                "demo.com",
                "sample.com",
                "localhost",
                "127.0.0.1",
            ]
        ):
            return False, 0.0

        # Check for noreply/system emails (usually not PII)
        if any(
            sys in lower_email
            for sys in [
                "noreply@",
                "no-reply@",
                "donotreply@",
                "system@",
                "admin@",
                "root@",
            ]
        ):
            confidence_adj = -0.3
        else:
            confidence_adj = 0.0

        # Context validation
        confidence_adj += self._check_context(context)

        return True, confidence_adj

    def validate_address(self, value: str, context: str = "") -> tuple[bool, float]:
        """
        Validate address with context.

        Args:
            value: The address detected
            context: Surrounding text context

        Returns:
            (is_valid, confidence_adjustment)
        """
        # Check for fake addresses
        lower_addr = value.lower()
        if any(
            fake in lower_addr
            for fake in [
                "123 main st",
                "123 fake st",
                "1234 test lane",
                "example address",
            ]
        ):
            return False, 0.0

        # Context validation
        confidence_adj = self._check_context(context)

        return True, confidence_adj

    def _check_context(self, context: str) -> float:
        """
        Check context for keywords and adjust confidence.

        Args:
            context: Surrounding text

        Returns:
            Confidence adjustment value
        """
        if not context:
            return 0.0

        adjustment = 0.0

        # Check for positive indicators
        if self.context_pattern.search(context):
            adjustment += CONTEXT_BOOST

        # Check for negative indicators
        if self.false_positive_pattern.search(context):
            adjustment -= FALSE_POSITIVE_PENALTY

        return adjustment

    def _luhn_check(self, digits: str) -> bool:
        """
        Perform Luhn algorithm check on credit card number.

        Args:
            digits: Credit card digits

        Returns:
            True if valid according to Luhn algorithm
        """
        if not digits or len(digits) < 13:
            return False

        try:
            total = 0
            reverse_digits = digits[::-1]

            for i, digit in enumerate(reverse_digits):
                n = int(digit)
                if i % 2 == 1:
                    n = n * 2
                    if n > 9:
                        n = n - 9
                total += n

            return total % 10 == 0
        except (ValueError, IndexError, TypeError):
            return False

    def validate_entity(
        self, entity_type: str, value: str, context: str = "", confidence: float = 1.0
    ) -> tuple[bool, float]:
        """
        Main validation entry point.

        Args:
            entity_type: Type of entity (ID, PHONE_NUMBER, etc.)
            value: The detected value
            context: Surrounding text context
            confidence: Original confidence score

        Returns:
            (is_valid, adjusted_confidence)
        """
        # Route to specific validator
        validators = {
            "ID": self.validate_id,
            "PHONE_NUMBER": self.validate_phone,
            "CREDIT_CARD": self.validate_credit_card,
            "EMAIL_ADDRESS": self.validate_email,
            "ADDRESS": self.validate_address,
        }

        validator = validators.get(entity_type)
        if validator:
            is_valid, confidence_adj = validator(value, context)
            if not is_valid:
                return False, 0.0
            new_confidence = confidence + confidence_adj
            # Clamp confidence between 0 and 1
            new_confidence = max(0.0, min(1.0, new_confidence))
            # Filter by minimum confidence
            if new_confidence < MIN_CONFIDENCE:
                return False, new_confidence
            return True, new_confidence

        # No specific validator, use general context check
        confidence_adj = self._check_context(context)
        new_confidence = confidence + confidence_adj
        new_confidence = max(0.0, min(1.0, new_confidence))

        if new_confidence < MIN_CONFIDENCE:
            return False, new_confidence

        return True, new_confidence
