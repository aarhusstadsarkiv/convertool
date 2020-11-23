# """Shared testing fixtures.
# """
# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import shutil
from pathlib import Path
from typing import Generator

import pytest

from convertool.database import FileDB

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
def test_out(test_data: Path) -> Generator[Path, None, None]:
    out_path: Path = test_data / "out"
    out_path.mkdir(exist_ok=True)
    yield out_path
    shutil.rmtree(out_path, ignore_errors=True)


@pytest.fixture
def test_pdf(test_files: Path) -> Path:
    return test_files / "test.pdf"


@pytest.fixture
def test_docx(test_files: Path) -> Path:
    return test_files / "test.docx"


@pytest.fixture
def test_jpg(test_files: Path) -> Path:
    return test_files / "test.jpg"


@pytest.fixture
def conv_json() -> Path:
    return (
        Path(__file__).parent.parent
        / "convertool"
        / "core"
        / "convert_map.json"
    )


@pytest.fixture
async def db_conn(test_data):
    file_db = FileDB(f"sqlite:///{test_data}/files.db")
    await file_db.connect()
    yield file_db
    file_db.converted_files.drop(file_db.engine, checkfirst=True)
    await file_db.disconnect()
