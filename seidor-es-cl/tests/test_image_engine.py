from presidio_image_redactor import ImageAnalyzerEngine

from seidor_cl.image_engine import EsImageAnalyzerEngine


def test_defaults_to_spanish(monkeypatch):
    seen = {}

    def fake(self, image, ocr_kwargs=None, **kw):
        seen.update(ocr=ocr_kwargs, kw=kw)
        return []

    monkeypatch.setattr(ImageAnalyzerEngine, "analyze", fake)
    EsImageAnalyzerEngine.analyze(object.__new__(EsImageAnalyzerEngine), "img")
    assert seen["ocr"] == {"lang": "spa"} and seen["kw"]["language"] == "es"


def test_caller_can_override(monkeypatch):
    seen = {}
    monkeypatch.setattr(ImageAnalyzerEngine, "analyze", lambda s, i, o=None, **kw: seen.update(ocr=o, kw=kw))
    EsImageAnalyzerEngine.analyze(object.__new__(EsImageAnalyzerEngine), "img", {"lang": "eng"}, language="en")
    assert seen["ocr"] == {"lang": "eng"} and seen["kw"]["language"] == "en"


import shutil
from pathlib import Path

import pytest
from PIL import Image


@pytest.mark.skipif(not shutil.which("tesseract"), reason="tesseract not installed (runs in the Docker image)")
def test_ocr_reads_scanned_fixture():
    png = Path(__file__).resolve().parents[1] / "fixtures" / "documento_escaneado_10.png"
    from seidor_cl.engine import build_analyzer

    engine = EsImageAnalyzerEngine(analyzer_engine=build_analyzer())
    results = engine.analyze(Image.open(png), score_threshold=0.4)
    assert "CL_RUT" in {r.entity_type for r in results}
