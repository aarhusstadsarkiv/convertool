# """Shared testing fixtures.
# """
# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
from pathlib import Path

import pytest

# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------


@pytest.fixture
def temp_dir(tmpdir_factory) -> Path:
    temp_dir: str = tmpdir_factory.mktemp("temp_dir")
    return Path(temp_dir)


@pytest.fixture
def test_data() -> Path:
    test_dir = Path(__file__).parent
    return test_dir / "test_data"


@pytest.fixture
def test_files(test_data: Path) -> Path:
    return test_data / "AARS.TEST"


@pytest.fixture
def test_out(test_data: Path) -> Path:
    return test_data / "out"


@pytest.fixture
def test_pdf(test_files: Path) -> Path:
    return test_files / "test.pdf"
