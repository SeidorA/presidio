import pytest
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngineProvider

from seidor_cl import ClRutRecognizer, is_valid_rut, rut_check_digit


@pytest.fixture(scope="module")
def analyzer():
    nlp = NlpEngineProvider(nlp_configuration={
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "es", "model_name": "es_core_news_lg"}],
    }).create_engine()
    registry = RecognizerRegistry(supported_languages=["es"])
    registry.add_recognizer(ClRutRecognizer())
    return AnalyzerEngine(nlp_engine=nlp, registry=registry, supported_languages=["es"])


def ruts(analyzer, text, min_score=0.0):
    res = analyzer.analyze(text, language="es", entities=["CL_RUT"])
    return [(text[r.start:r.end], r.score) for r in res if r.score >= min_score]


@pytest.mark.parametrize("rut", ["12.345.678-5", "12345678-5", "11.111.111-1", "7.654.321-6"])
def test_valid_formats(rut):
    assert is_valid_rut(rut)


def test_known_dv_and_k():
    assert rut_check_digit(12345678) == "5"
    assert rut_check_digit(7654321) == "6"
    # body with remainder 10 -> K
    body = next(b for b in range(6_000_000, 6_000_200) if rut_check_digit(b) == "K")
    assert is_valid_rut(f"{body}-K") and is_valid_rut(f"{body}-k")
    assert is_valid_rut(f"{body}K")


def test_dv_zero():
    body = next(b for b in range(6_000_000, 6_000_200) if rut_check_digit(b) == "0")
    assert is_valid_rut(f"{body}-0")


@pytest.mark.parametrize("rut", ["12.345.678-4", "12345678-K", "123", "0-0", "00000000-0", "abc"])
def test_invalid_rejected(rut):
    assert not is_valid_rut(rut)


def test_detect_with_dots(analyzer):
    assert ruts(analyzer, "Mi RUT es 12.345.678-5.")[0][0] == "12.345.678-5"


def test_detect_with_hyphen_only(analyzer):
    assert ruts(analyzer, "RUT 12345678-5")[0][0] == "12345678-5"


def test_detect_plain_with_context_above_threshold(analyzer):
    found = ruts(analyzer, "El rol único tributario es 123456785", min_score=0.4)
    assert found and found[0][0] == "123456785"


def test_plain_without_context_is_low_score(analyzer):
    assert not ruts(analyzer, "Código interno 123456785", min_score=0.4)


def test_invalid_dv_not_detected(analyzer):
    assert not ruts(analyzer, "RUT 12.345.678-4")


def test_invoice_numbers_not_flagged(analyzer):
    text = "Factura N° 48201937 por $ 1.250.000 orden 55512345"
    assert not ruts(analyzer, text, min_score=0.4)


def test_dotted_scores_higher_than_plain(analyzer):
    dotted = ruts(analyzer, "RUT 12.345.678-5")[0][1]
    plain = ruts(analyzer, "RUT 123456785")[0][1]
    assert dotted > plain
