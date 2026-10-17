"""Seidor extensions for Presidio: Spanish + Chile recognizers (no core changes)."""
from .cl_phone_recognizer import ClPhoneRecognizer
from .cl_rut_recognizer import ClRutRecognizer, is_valid_rut, rut_check_digit
from .es_health_recognizer import EsHealthTermRecognizer, Icd10Recognizer


def cl_recognizers(language: str = "es"):
    """Return the custom recognizers for the given language."""
    return [
        ClRutRecognizer(supported_language=language),
        ClPhoneRecognizer(supported_language=language),
        EsHealthTermRecognizer(supported_language=language),
        Icd10Recognizer(supported_language=language),
    ]


def register_cl_recognizers(registry, language: str = "es"):
    """Add the custom recognizers to an existing RecognizerRegistry."""
    for recognizer in cl_recognizers(language):
        registry.add_recognizer(recognizer)
    return registry


__all__ = [
    "ClRutRecognizer", "ClPhoneRecognizer", "EsHealthTermRecognizer",
    "Icd10Recognizer", "cl_recognizers", "register_cl_recognizers",
    "is_valid_rut", "rut_check_digit",
]
