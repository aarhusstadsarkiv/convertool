import pytest
import os
import sys
import shutil
from unittest.mock import patch
from pathlib import Path
from convertool.convert import calc_timeout, check_errors, convert_files
from convertool.utils import get_files
from convertool.exceptions import ConversionError


@pytest.fixture
def file_handler():
    script_path = os.path.dirname(os.path.realpath(__file__))
    test_path = os.path.join(script_path, "test_data")
    valid_path = os.path.join(test_path, "data")
    out_path = os.path.join(test_path, "out")
    file = get_files(valid_path)[0]
    yield out_path, file
    for file in os.listdir(out_path):
        try:
            os.remove(os.path.join(out_path, file))
        except IsADirectoryError:
            shutil.rmtree(os.path.join(out_path, file))


class TestAuxFunctions:
    def test_calc_timeout(self):
        assert calc_timeout(Path("bogus"), 0) == 0

    def test_check_errors(self):
        assert check_errors(err_count=0, max_errs=1) == ""
        errs = 3
        max_errs = 2
        assert (
            f"Error count {errs} is higher than threshold of {max_errs}"
            in check_errors(err_count=errs, max_errs=max_errs)
        )


class TestConvertFiles:
    def test_with_valid_input(self, file_handler, caplog):
        out, file = file_handler
        convert_files("libre", [file], out)
        assert "Started conversion of 1 files" in caplog.text
        assert "Now converting using LibreOffice" in caplog.text
        assert "Finished conversion of 1 files with 0 issues" in caplog.text

    def test_with_no_files(self, file_handler, caplog):
        out, file = file_handler
        with pytest.raises(ConversionError):
            convert_files("libre", [], out)
        assert "Got no files to convert!" in caplog.text

    def test_parents(self, file_handler, caplog):
        out, file = file_handler
        # Our test file does indeed have two parents, things go well
        convert_files("libre", [file], out, parents=2)
        assert "Started conversion of 1 files" in caplog.text
        assert "Now converting using LibreOffice" in caplog.text
        assert "Finished conversion of 1 files with 0 issues" in caplog.text
        # It definitely does not have sys.maxsize parents though
        with pytest.raises(ConversionError):
            convert_files("libre", [file], out, parents=sys.maxsize)
        assert (
            f"Parent index {sys.maxsize} out of range for {file}"
            in caplog.text
        )

    def test_libre_convert(self, file_handler, caplog):
        out, file = file_handler
        fail_file = "bogus"
        # Fail
        with pytest.raises(ConversionError):
            convert_files("libre", [fail_file], out)
        assert f"LibreConvert of {fail_file} failed with error:" in caplog.text
        assert "Error count 1 is higher than threshold of 0" in caplog.text
        with patch("convertool.convert.calc_timeout", return_value=0):
            convert_files("libre", [file], out)
        assert (
            f"LibreConvert of {file} timed out after 0 seconds" in caplog.text
        )
