"""Dockerized image-redactor entrypoint: Spanish OCR (tesseract spa) + Spanish analyzer."""
from app import Server  # presidio-image-redactor/app.py, unmodified
from presidio_image_redactor import ImageAnalyzerEngine, ImageRedactorEngine

from seidor_cl.engine import build_analyzer


class EsImageAnalyzerEngine(ImageAnalyzerEngine):
    """Defaults to language 'es' and OCR language 'spa'."""

    def analyze(self, image, ocr_kwargs=None, **text_analyzer_kwargs):  # noqa: D102
        text_analyzer_kwargs.setdefault("language", "es")
        ocr_kwargs = {"lang": "spa", **(ocr_kwargs or {})}
        return super().analyze(image, ocr_kwargs, **text_analyzer_kwargs)


def build_engine() -> ImageRedactorEngine:  # noqa: D103
    return ImageRedactorEngine(EsImageAnalyzerEngine(analyzer_engine=build_analyzer()))


def create_app():  # noqa: D103
    server = Server()
    server.engine = build_engine()
    return server.app
