# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import json
import math
import shutil
from pathlib import Path

import pytest
from acamodels import ArchiveFile

import convertool.core.convert as c_convert
from convertool.core.convert import FileConv
from convertool.database import FileDB
from convertool.exceptions import ConversionError
from convertool.exceptions import ImageError
from convertool.exceptions import LibreError

# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------
pytestmark = pytest.mark.asyncio

# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------


class TestFileConv:
    def test_init(self, test_pdf, temp_dir):
        file_list = [ArchiveFile(path=test_pdf)]
        file_conv = FileConv(files=file_list, out_dir=temp_dir)
        assert file_conv.files == file_list
        assert file_conv.out_dir == temp_dir

    def test_validators(self, test_pdf, temp_dir):
        file_list = [ArchiveFile(path=test_pdf)]
        file_conv = FileConv(files=file_list, out_dir=temp_dir)
        assert file_conv.max_errs == int(math.sqrt(len(file_list)))
        file_conv = FileConv(files=file_list, out_dir=temp_dir, max_errs=2)
        assert file_conv.max_errs == 2
        file_conv = FileConv(files=file_list, out_dir=temp_dir, max_errs=None)
        assert file_conv.max_errs == int(math.sqrt(len(file_list)))

    def test_conv_map(self, test_pdf, temp_dir, conv_json):
        file_list = [ArchiveFile(path=test_pdf)]
        file_conv = FileConv(files=file_list, out_dir=temp_dir)
        with conv_json.open(encoding="utf-8") as f:
            assert file_conv.conv_map() == json.load(f)

    async def test_convert(self, db_conn, test_out, caplog, monkeypatch):
        file_db: FileDB = db_conn
        files = await file_db.get_files()
        file_conv = FileConv(files=files, out_dir=test_out)
        file_conv.convert()
        assert "Started conversion of 3 files" in caplog.text
        assert (
            "Finished conversion of 3 files with 0 issues, "
            "0 of which were critical."
        ) in caplog.text

        # Exceptions

        # Libre fails
        def libre_fail(*args, **kwargs):
            raise LibreError("Libre fail")

        # Libre warning
        def libre_warn(*args, **kwargs):
            raise LibreError("Libre timeout", timeout=True)

        monkeypatch.setattr(c_convert, "libre_convert", libre_fail)
        file_conv.convert()
        assert "Libre fail" in caplog.text

        monkeypatch.setattr(c_convert, "libre_convert", libre_warn)
        file_conv.convert()
        assert "Libre timeout" in caplog.text
        monkeypatch.undo()

        # shutil.copy2 fails
        def shutil_fail(*args, **kwargs):
            raise OSError("shutil fail")

        monkeypatch.setattr(shutil, "copy2", shutil_fail)
        file_conv.convert()
        assert "shutil fail" in caplog.text
        monkeypatch.undo()

        # image conversion fails
        def img_fail(*args, **kwargs):
            raise ImageError("img2tif fail")

        monkeypatch.setattr(c_convert, "img2tif", img_fail)
        file_conv.convert()
        assert "img2tif fail" in caplog.text

        # Too many errors, tif still fails
        file_conv.max_errs = 0
        err_match = "Error count 1 is higher than threshold of 0"
        with pytest.raises(ConversionError, match=err_match):
            file_conv.convert()
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
