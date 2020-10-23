# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import pytest
from pydantic import BaseModel
from pydantic import ValidationError

from convertool.database import db
from convertool.database import FileDB
from convertool.exceptions import FileParseError

# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------
pytestmark = pytest.mark.asyncio


@pytest.fixture
async def db_conn(test_data):
    file_db = FileDB(f"sqlite:///{test_data}/files.db")
    await file_db.connect()
    yield file_db
    await file_db.disconnect()


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------


class TestFileDB:
    async def test_init(self, test_data):
        file_db = FileDB(f"sqlite:///{test_data}/files.db")
        await file_db.connect()
        await file_db.disconnect()

    async def test_get_files(self, db_conn, monkeypatch):
        file_db: FileDB = db_conn

        # Normal operation
        files = await file_db.get_files()
        for archive_file in files:
            assert archive_file.path.is_file()
            assert archive_file.uuid is not None
            assert archive_file.checksum is not None
            assert archive_file.puid is not None
            assert archive_file.signature is not None

        # Validation error
        def raise_val_error(*args):
            raise ValidationError("test", BaseModel)

        monkeypatch.setattr(db, "parse_obj_as", raise_val_error)
        with pytest.raises(FileParseError):
            await file_db.get_files()
