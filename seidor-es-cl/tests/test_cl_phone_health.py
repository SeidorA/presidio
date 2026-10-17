import pytest



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


@pytest.mark.parametrize("text", [
    "Factura 12345678901234",
    "Codigo 5698765432101",
    "Total 1.234.567",
    "Fecha 2026-10-17",
])
def test_phone_negatives(analyzer, text):
    assert not found(analyzer, text, "CL_PHONE_NUMBER")
