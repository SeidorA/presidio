import pytest
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngineProvider

from seidor_cl import cl_recognizers


@pytest.fixture(scope="module")
def analyzer():
    nlp = NlpEngineProvider(nlp_configuration={
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "es", "model_name": "es_core_news_lg"}],
    }).create_engine()
    registry = RecognizerRegistry(supported_languages=["es"])
    for r in cl_recognizers():
        registry.add_recognizer(r)
    return AnalyzerEngine(nlp_engine=nlp, registry=registry, supported_languages=["es"])


def found(analyzer, text, entity):
    return [text[r.start:r.end] for r in analyzer.analyze(text, "es", entities=[entity])]


@pytest.mark.parametrize("n", ["+56 9 8765 4321", "+56987654321", "56 9 1234 5678"])
def test_mobile(analyzer, n):
    assert n in found(analyzer, f"Llámame al {n} por favor", "CL_PHONE_NUMBER")


def test_landline(analyzer):
    assert "+56 2 2345 6789" in found(analyzer, "Oficina +56 2 2345 6789", "CL_PHONE_NUMBER")


def test_icd10_with_context(analyzer):
    assert "J45.9" in found(analyzer, "Diagnóstico CIE-10 J45.9", "ICD10_CODE")


def test_health_terms(analyzer):
    got = [t.lower() for t in found(analyzer, "Licencia médica por Fonasa e isapre, receta adjunta", "ES_HEALTH_TERM")]
    assert {"licencia médica", "fonasa", "isapre", "receta"} <= set(got)
