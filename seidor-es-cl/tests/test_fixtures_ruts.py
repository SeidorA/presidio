"""Fixtures: manifest consistency and end-to-end detection through the analyzer."""
import json
from pathlib import Path

import fitz
import pytest
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngineProvider

from seidor_cl import cl_recognizers, is_valid_rut

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
MANIFEST = json.loads((FIXTURES / "manifest.json").read_text())
# The scanned PDF has no text layer; it is covered by the image-redactor OCR test.
TEXT_FIXTURES = {k: v for k, v in MANIFEST.items() if "escaneado" not in k}


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


def read(name):
    path = FIXTURES / name
    if path.suffix == ".pdf":
        return "\n".join(p.get_text() for p in fitz.open(path))
    return path.read_text(encoding="utf-8")


@pytest.mark.parametrize("fname,entry", MANIFEST.items())
def test_manifest_consistency(fname, entry):
    assert all(is_valid_rut(r) for r in entry["valid_ruts"])
    assert not any(is_valid_rut(r) for r in entry["invalid_ruts"])


@pytest.mark.parametrize("fname,entry", TEXT_FIXTURES.items())
def test_ruts_detected_through_analyzer(analyzer, fname, entry):
    text = read(fname)
    results = analyzer.analyze(text, "es", entities=["CL_RUT"])
    strong = {text[r.start:r.end] for r in results if r.score >= 0.4}
    any_score = {text[r.start:r.end] for r in results}
    formatted = {r for r in entry["valid_ruts"] if "-" in r}
    # Known limitation: a bare RUT (no hyphen) in a CSV cell has no nearby context
    # word (the header is too far), so it is detected but stays below 0.4.
    assert formatted <= strong
    assert set(entry["valid_ruts"]) <= any_score
    assert not (set(entry["invalid_ruts"]) & any_score)
