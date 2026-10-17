"""Chilean RUT/RUN recognizer (modulo 11 check digit)."""
import re
from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer

MIN_BODY = 1_000_000
MAX_BODY = 99_999_999


def rut_check_digit(body: int) -> str:
    """Return the modulo 11 check digit ('0'-'9' or 'K') for a RUT body."""
    total, factor = 0, 2
    for digit in reversed(str(body)):
        total += int(digit) * factor
        factor = 2 if factor == 7 else factor + 1
    remainder = 11 - total % 11
    if remainder == 11:
        return "0"
    if remainder == 10:
        return "K"
    return str(remainder)


def is_valid_rut(text: str) -> bool:
    """Validate a RUT string with or without dots and hyphen."""
    clean = re.sub(r"[.\-\s]", "", text).upper()
    if not re.fullmatch(r"\d{7,8}[\dK]", clean):
        return False
    body, dv = int(clean[:-1]), clean[-1]
    if not MIN_BODY <= body <= MAX_BODY:
        return False
    return rut_check_digit(body) == dv


class ClRutRecognizer(PatternRecognizer):
    """Recognize Chilean RUT/RUN with check digit validation.

    Invalid check digits are discarded. Bare digit strings (no dots/hyphen) keep a
    very low score and only become relevant when context words are nearby, to avoid
    flagging invoice or order numbers.
    """

    COUNTRY_CODE = "cl"

    PATTERNS = [
        Pattern("RUT con puntos y guion", r"\b\d{1,2}\.\d{3}\.\d{3}\s?-\s?[\dkK]\b", 0.85),
        Pattern("RUT con guion", r"\b\d{7,8}\s?-\s?[\dkK]\b", 0.75),
        Pattern("RUT con K sin guion", r"\b\d{7,8}[kK]\b", 0.3),
        Pattern("RUT solo digitos", r"\b\d{8,9}\b", 0.05),
    ]

    CONTEXT = [
        "rut", "run", "rol", "unico", "único", "tributario",
        "cédula", "cedula", "identidad",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "es",
        supported_entity: str = "CL_RUT",
        name: Optional[str] = None,
    ):
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns or self.PATTERNS,
            context=context or self.CONTEXT,
            supported_language=supported_language,
            name=name,
        )

    def validate_result(self, pattern_text: str) -> Optional[bool]:  # noqa: D102
        # False drops the match; None keeps the pattern score (no 1.0 boost).
        return None if is_valid_rut(pattern_text) else False
