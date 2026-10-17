"""Dockerized image-redactor entrypoint: Spanish OCR (tesseract spa) + Spanish analyzer."""
from app import Server  # presidio-image-redactor/app.py, unmodified
from presidio_image_redactor import ImageRedactorEngine

from seidor_cl.engine import build_analyzer
from seidor_cl.image_engine import EsImageAnalyzerEngine


def build_engine() -> ImageRedactorEngine:  # noqa: D103
    return ImageRedactorEngine(EsImageAnalyzerEngine(analyzer_engine=build_analyzer()))


def create_app():  # noqa: D103
    server = Server()
    server.engine = build_engine()
    return server.app
