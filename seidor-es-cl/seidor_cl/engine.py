"""Shared Spanish AnalyzerEngine factory (library use: Streamlit demo, image-redactor)."""
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngineProvider

from seidor_cl import register_cl_recognizers


def build_analyzer(model_name: str = "es_core_news_lg") -> AnalyzerEngine:
    """Build an es AnalyzerEngine with predefined + Chile recognizers."""
    nlp = NlpEngineProvider(nlp_configuration={
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "es", "model_name": model_name}],
        "ner_model_configuration": {
            "model_to_presidio_entity_mapping": {"PER": "PERSON", "LOC": "LOCATION", "ORG": "ORGANIZATION"},
            "labels_to_ignore": ["MISC"],
        },
    }).create_engine()
    registry = RecognizerRegistry(supported_languages=["es"])
    registry.load_predefined_recognizers(languages=["es"], nlp_engine=nlp)
    register_cl_recognizers(registry, "es")
    return AnalyzerEngine(nlp_engine=nlp, registry=registry, supported_languages=["es"])
