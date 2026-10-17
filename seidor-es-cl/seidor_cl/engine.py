"""Shared Spanish AnalyzerEngine factory (library use: Streamlit demo, image-redactor)."""
import os
from pathlib import Path

from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngineProvider

from seidor_cl import register_cl_recognizers

DEFAULT_NLP_CONF = Path(__file__).resolve().parents[1] / "conf" / "nlp_es.yaml"


def build_analyzer(nlp_conf_file: str = "") -> AnalyzerEngine:
    """Build an es AnalyzerEngine (predefined + Chile recognizers) from conf/nlp_es.yaml."""
    conf = nlp_conf_file or os.environ.get("SEIDOR_NLP_CONF_FILE") or str(DEFAULT_NLP_CONF)
    nlp = NlpEngineProvider(conf_file=conf).create_engine()
    registry = RecognizerRegistry(supported_languages=["es"])
    registry.load_predefined_recognizers(languages=["es"], nlp_engine=nlp)
    register_cl_recognizers(registry, "es")
    return AnalyzerEngine(nlp_engine=nlp, registry=registry, supported_languages=["es"])
