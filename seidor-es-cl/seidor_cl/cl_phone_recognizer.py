"""Chilean phone number recognizer."""
from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class ClPhoneRecognizer(PatternRecognizer):
    """Recognize Chilean mobile (+56 9 ...) and Santiago landline (+56 2 ...) numbers."""

    COUNTRY_CODE = "cl"

    PATTERNS = [
        Pattern("Movil con +56", r"(?<!\w)\+?56[\s-]?9[\s-]?\d{4}[\s-]?\d{4}\b", 0.7),
        Pattern("Fijo RM con +56", r"(?<!\w)\+56[\s-]?2[\s-]?\d{4}[\s-]?\d{4}\b", 0.6),
        Pattern("Movil 9 XXXX XXXX", r"(?<!\w)9[\s-]\d{4}[\s-]\d{4}\b", 0.3),
        Pattern("Movil 9 digitos", r"(?<!\w)9\d{8}\b", 0.05),
    ]

    CONTEXT = [
        "teléfono", "telefono", "fono", "celular", "cel", "móvil", "movil",
        "whatsapp", "contacto", "llamar",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "es",
        supported_entity: str = "CL_PHONE_NUMBER",
        name: Optional[str] = None,
    ):
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns or self.PATTERNS,
            context=context or self.CONTEXT,
            supported_language=supported_language,
            name=name,
        )
