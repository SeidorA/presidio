"""Dockerized image-redactor entrypoint: Spanish OCR (tesseract spa) + Spanish analyzer."""
from app import Server  # presidio-image-redactor/app.py, unmodified
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_image_redactor import ImageAnalyzerEngine, ImageRedactorEngine

from seidor_cl import register_cl_recognizers


class EsImageAnalyzerEngine(ImageAnalyzerEngine):
    """Defaults to language 'es' and OCR language 'spa'."""

    def analyze(self, image, ocr_kwargs=None, **text_analyzer_kwargs):  # noqa: D102
        text_analyzer_kwargs.setdefault("language", "es")
        ocr_kwargs = {"lang": "spa", **(ocr_kwargs or {})}
        return super().analyze(image, ocr_kwargs, **text_analyzer_kwargs)


def build_engine() -> ImageRedactorEngine:  # noqa: D103
    nlp = NlpEngineProvider(nlp_configuration={
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "es", "model_name": "es_core_news_lg"}],
    }).create_engine()
    registry = RecognizerRegistry(supported_languages=["es"])
    registry.load_predefined_recognizers(languages=["es"], nlp_engine=nlp)
    register_cl_recognizers(registry, "es")
    analyzer = AnalyzerEngine(nlp_engine=nlp, registry=registry, supported_languages=["es"])
    return ImageRedactorEngine(EsImageAnalyzerEngine(analyzer_engine=analyzer))


def create_app():  # noqa: D103
    server = Server()
    server.engine = build_engine()
    return server.app
