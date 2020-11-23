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

# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------


class TestFileDB:
    async def test_init(self, test_data):
        file_db = FileDB(f"sqlite:///{test_data}/files.db")
        await file_db.connect()
        await file_db.disconnect()

    async def test_init_files(self, db_conn, monkeypatch):
        file_db: FileDB = db_conn

        # Normal operation
        files = await file_db.get_files()
        for archive_file in files:
            print(archive_file)
            assert archive_file.path.is_file()
            assert archive_file.uuid is not None
            assert archive_file.checksum is not None
            assert archive_file.puid is not None
            assert archive_file.signature is not None

        # Validation error
        def raise_val_error(*args, **kwargs):
            raise ValidationError("test", BaseModel)

        monkeypatch.setattr(db, "parse_obj_as", raise_val_error)
        with pytest.raises(FileParseError):
            await file_db.get_files()

    async def test_update_status(self, db_conn):
        file_db: FileDB = db_conn
        files = await file_db.get_files()
        await file_db.update_status(files[0].uuid)
        converted_files = await file_db.fetch_all(
            file_db.converted_files.select()
        )
        assert len(converted_files) == 1
        assert str(files[0].uuid) in dict(converted_files[0]).values()
        # Len should stay the same
        await file_db.update_status(files[0].uuid)
        converted_files = await file_db.fetch_all(
            file_db.converted_files.select()
        )
        assert len(converted_files) == 1
