"""EXPERIMENTAL: Spanish health term and ICD-10 (CIE-10) recognizers."""
from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer

HEALTH_TERMS = (
    r"diagn[óo]stico|licencia\s+m[ée]dica|receta(?:\s+m[ée]dica)?|isapre|fonasa"
    r"|ficha\s+cl[íi]nica|certificado\s+m[ée]dico"
)


class EsHealthTermRecognizer(PatternRecognizer):
    """EXPERIMENTAL. Flags health-related terms (keyword based, high FP risk)."""

    PATTERNS = [Pattern("Termino de salud", rf"\b(?:{HEALTH_TERMS})\b", 0.4)]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "es",
        supported_entity: str = "ES_HEALTH_TERM",
        name: Optional[str] = "EsHealthTermRecognizer (experimental)",
    ):
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns or self.PATTERNS,
            context=context,
            supported_language=supported_language,
            name=name,
        )


class Icd10Recognizer(PatternRecognizer):
    """EXPERIMENTAL. ICD-10 (CIE-10) codes such as J45.9; needs context to be useful."""

    PATTERNS = [
        Pattern("CIE-10 con decimal", r"\b[A-TV-Z]\d{2}\.\d{1,2}\b", 0.3),
        Pattern("CIE-10 sin decimal", r"\b[A-TV-Z]\d{2}\b", 0.05),
    ]
    CONTEXT = ["cie-10", "cie10", "cie", "diagnóstico", "diagnostico", "dg", "código"]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "es",
        supported_entity: str = "ICD10_CODE",
        name: Optional[str] = "Icd10Recognizer (experimental)",
    ):
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns or self.PATTERNS,
            context=context or self.CONTEXT,
            supported_language=supported_language,
            name=name,
        )
