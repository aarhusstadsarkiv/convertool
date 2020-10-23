# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import math

from acamodels import ArchiveFile

from convertool.core.internals import FileConv


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------


class TestFileConv:
    def test_init(self, test_pdf, temp_dir):
        file_list = [ArchiveFile(path=test_pdf)]
        file_conv = FileConv(
            files=file_list, out_dir=temp_dir, convert_to="odt"
        )
        assert file_conv.files == file_list
        assert file_conv.out_dir == temp_dir
        assert file_conv.convert_to == "odt"

    def test_validators(self, test_pdf, temp_dir):
        file_list = [ArchiveFile(path=test_pdf)]
        file_conv = FileConv(
            files=file_list, out_dir=temp_dir, convert_to="odt"
        )
        assert file_conv.max_errs == int(math.sqrt(len(file_list)))
        file_conv = FileConv(
            files=file_list, out_dir=temp_dir, convert_to="odt", max_errs=2
        )
        assert file_conv.max_errs == 2
        file_conv = FileConv(
            files=file_list, out_dir=temp_dir, convert_to="odt", max_errs=None
        )
        assert file_conv.max_errs == int(math.sqrt(len(file_list)))
