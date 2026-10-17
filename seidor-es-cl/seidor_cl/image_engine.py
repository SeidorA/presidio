"""Image analyzer defaulting to Spanish (text language 'es', Tesseract 'spa')."""
from presidio_image_redactor import ImageAnalyzerEngine


class EsImageAnalyzerEngine(ImageAnalyzerEngine):
    """Defaults to language 'es' and OCR language 'spa'; callers can override both."""

    def analyze(self, image, ocr_kwargs=None, **text_analyzer_kwargs):  # noqa: D102
        text_analyzer_kwargs.setdefault("language", "es")
        ocr_kwargs = {"lang": "spa", **(ocr_kwargs or {})}
        return super().analyze(image, ocr_kwargs, **text_analyzer_kwargs)
