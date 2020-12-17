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
            assert archive_file.path.is_file()
            assert archive_file.uuid is not None
            assert archive_file.checksum is not None
            if archive_file.aars_path.name != "test.empty":
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

    async def test_check_status(self, db_conn):
        file_db: FileDB = db_conn
        files = await file_db.get_files()
        for file in files:
            assert await file_db.check_status(file.uuid) is False
        await file_db.update_status(files[0].uuid)
        assert await file_db.check_status(files[0].uuid) is True

    async def test_converted_uuids(self, db_conn):
        file_db: FileDB = db_conn
        files = await file_db.get_files()
        await file_db.update_status(files[0].uuid)
        uuids = await file_db.converted_uuids()
        assert files[0].uuid in uuids
        assert files[1].uuid not in uuids
