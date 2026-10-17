"""Every valid RUT in the synthetic fixtures must be found; invalid ones must not."""
import json
from pathlib import Path

import pytest

from seidor_cl import is_valid_rut

MANIFEST = json.loads((Path(__file__).resolve().parents[1] / "fixtures" / "manifest.json").read_text())


@pytest.mark.parametrize("fname,entry", MANIFEST.items())
def test_manifest_consistency(fname, entry):
    assert all(is_valid_rut(r) for r in entry["valid_ruts"])
    assert not any(is_valid_rut(r) for r in entry["invalid_ruts"])
