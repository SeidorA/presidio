import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture(scope="session")
def analyzer():
    from seidor_cl.engine import build_analyzer

    return build_analyzer()
