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
