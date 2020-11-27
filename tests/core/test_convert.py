# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import json
import math
from pathlib import Path

import pytest
from acamodels import ArchiveFile

import convertool.core.convert as c_convert
from convertool.core.convert import FileConv
from convertool.database import FileDB
from convertool.exceptions import ConversionError
from convertool.exceptions import GSError
from convertool.exceptions import ImageError
from convertool.exceptions import LibreError

# import shutil

# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------
pytestmark = pytest.mark.asyncio

# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------


class TestFileConv:
    def test_init(self, test_pdf, temp_dir, db_conn):
        file_list = [ArchiveFile(path=test_pdf)]
        file_conv = FileConv(files=file_list, out_dir=temp_dir, db=db_conn)
        assert file_conv.files == file_list
        assert file_conv.out_dir == temp_dir

    def test_validators(self, test_pdf, temp_dir, db_conn):
        file_list = [ArchiveFile(path=test_pdf)]
        file_conv = FileConv(files=file_list, out_dir=temp_dir, db=db_conn)
        assert file_conv.max_errs == int(math.sqrt(len(file_list)))
        file_conv = FileConv(
            files=file_list, out_dir=temp_dir, db=db_conn, max_errs=2
        )
        assert file_conv.max_errs == 2
        file_conv = FileConv(
            files=file_list, out_dir=temp_dir, db=db_conn, max_errs=None
        )
        assert file_conv.max_errs == int(math.sqrt(len(file_list)))

    def test_conv_map(self, test_pdf, temp_dir, conv_json, db_conn):
        file_list = [ArchiveFile(path=test_pdf)]
        file_conv = FileConv(files=file_list, out_dir=temp_dir, db=db_conn)
        with conv_json.open(encoding="utf-8") as f:
            assert file_conv.conv_map() == json.load(f)


class TestConvert:
    @pytest.fixture
    async def file_conv(self, db_conn, test_out):
        file_db: FileDB = db_conn
        files = await file_db.get_files()
        return FileConv(files=files, out_dir=test_out, db=file_db)

    @pytest.fixture
    async def conv_files(self, file_conv):
        files = file_conv.db.fetch_all(file_conv.db.converted_files.select())
        return files

    async def test_success_files(self, file_conv, caplog):
        await file_conv.convert()
        assert "Started conversion of 3 files" in caplog.text
        assert (
            "Finished conversion of 3 files with 0 issues, "
            "0 of which were critical."
        ) in caplog.text

    # Exceptions
    async def test_libre_fail(
        self, file_conv, monkeypatch, caplog, conv_files
    ):
        libre_file_uuid = "e93d2c29-b143-4c29-a135-f4a0feefee14"

        # Libre fails
        def libre_fail(*args, **kwargs):
            raise LibreError("Libre fail")

        monkeypatch.setattr(c_convert, "libre_convert", libre_fail)
        await file_conv.convert()
        converted_files = dict(await conv_files)
        assert libre_file_uuid not in converted_files.values()
        assert "Libre fail" in caplog.text

    async def test_libre_warn(
        self, file_conv, monkeypatch, caplog, conv_files
    ):
        libre_file_uuid = "e93d2c29-b143-4c29-a135-f4a0feefee14"

        # Libre warning
        def libre_warn(*args, **kwargs):
            raise LibreError("Libre timeout", timeout=True)

        monkeypatch.setattr(c_convert, "libre_convert", libre_warn)
        await file_conv.convert()
        converted_files = dict(await conv_files)
        assert libre_file_uuid not in converted_files.values()
        assert "Libre timeout" in caplog.text

    async def test_pdf_fail(self, file_conv, monkeypatch, caplog, conv_files):
        pdf_file_uuid = "93ba3862-a425-42bb-87ac-5c7912aa1a28"

        # Ghostscript fails
        def gs_fail(*args, **kwargs):
            raise GSError("gs fail")

        monkeypatch.setattr(c_convert, "convert_pdf", gs_fail)
        await file_conv.convert()
        converted_files = dict(await conv_files)
        assert pdf_file_uuid not in converted_files.values()
        assert "gs fail" in caplog.text

    async def test_image_fail(
        self, file_conv, monkeypatch, caplog, conv_files
    ):
        image_file_uuid = "a23d1ae1-42ec-4e5c-aa28-68b84b950cec"

        # image conversion fails
        def img_fail(*args, **kwargs):
            raise ImageError("img2tif fail")

        monkeypatch.setattr(c_convert, "img2tif", img_fail)
        await file_conv.convert()
        converted_files = dict(await conv_files)
        assert image_file_uuid not in converted_files.values()
        assert "img2tif fail" in caplog.text

    async def test_too_many_errs(self, file_conv, monkeypatch, caplog):
        # Too many errors
        def bad_errors(*args, **kwargs):
            return "Many errors! Handle it!"

        monkeypatch.setattr(c_convert, "check_errors", bad_errors)
        err_match = "Many errors! Handle it!"
        with pytest.raises(ConversionError, match=err_match):
            await file_conv.convert()
            assert err_match in caplog.text


class TestAuxFunctions:
    def test_calc_timeout(self, monkeypatch, temp_dir):
        test_file: Path = temp_dir / "test"
        test_file.touch()
        test_file.write_text("test" * 1000000)
        timeout = c_convert.calc_timeout(test_file)
        assert timeout == 13

        # File Not Found
        not_found = Path("not_a_file")
        timeout = c_convert.calc_timeout(not_found)
        assert timeout == 10

    def test_check_errors(self):
        assert c_convert.check_errors(1, 100) is None
        assert (
            c_convert.check_errors(100, 1) == "Error count 100 is higher than "
            "threshold of 1"
        )
