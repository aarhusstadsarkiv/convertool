# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import math
import sys

import pytest

from convertool.internals import create_outdir
from convertool.internals import File
from convertool.internals import FileConv


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------


class TestFile:
    def test_init(self, test_pdf):
        pdf_file = File(path=test_pdf)
        assert pdf_file.path == test_pdf
        assert pdf_file.encoding is None
        assert pdf_file.parent_dirs == 0

    def test_methods(self, test_pdf, temp_dir):
        pdf_file = File(path=test_pdf, parent_dirs=1)
        file_outdir = pdf_file.get_file_outdir(temp_dir)
        assert file_outdir == temp_dir / "AARS.TEST"


class TestFileConv:
    def test_init(self, test_pdf, temp_dir):
        file_list = [File(path=test_pdf)]
        file_conv = FileConv(
            files=file_list, out_dir=temp_dir, convert_to="odt"
        )
        assert file_conv.files == file_list
        assert file_conv.out_dir == temp_dir
        assert file_conv.convert_to == "odt"

    def test_validators(self, test_pdf, temp_dir):
        file_list = [File(path=test_pdf)]
        file_conv = FileConv(
            files=file_list, out_dir=temp_dir, convert_to="odt"
        )
        assert file_conv.max_errs == int(math.sqrt(len(file_list)))
        file_conv = FileConv(
            files=file_list, out_dir=temp_dir, convert_to="odt", max_errs=2
        )
        assert file_conv.max_errs == 2


class TestAuxFunctions:
    def test_create_outdir(self, test_pdf, temp_dir):
        outdir = create_outdir(test_pdf, temp_dir, parents=1)
        assert outdir == temp_dir / "AARS.TEST"
        with pytest.raises(
            IndexError,
            match=f"Parent index {sys.maxsize} out of range for {test_pdf}",
        ):
            create_outdir(test_pdf, temp_dir, parents=sys.maxsize)
