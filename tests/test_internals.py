import math
from pathlib import Path

from pydantic import ValidationError

import pytest
from convertool.internals import File, FileConv


class TestFile:
    def test_init(self, file_handler):
        _, file_path = file_handler

        # Required only
        file_0 = File(path=file_path)
        assert file_0.path == Path(file_path)
        assert file_0.encoding is None
        assert file_0.parent_dirs == 0

        # With optional
        file_1 = File(path=file_path, encoding=2, parent_dirs=2)
        assert file_1.path == Path(file_path)
        assert file_1.encoding == 2
        assert file_1.parent_dirs == 2

        # Path is not a file
        with pytest.raises(ValidationError, match="File does not exist"):
            File(path="Not a file")

    def test_get_file_outdir(self, file_handler):
        out_path, file_path = file_handler
        file = File(path=file_path)
        file_out = file.get_file_outdir(Path(out_path))
        assert file_out == Path(out_path)
        file = File(path=file_path, parent_dirs=2)
        file_out = file.get_file_outdir(Path(out_path))
        assert (
            file_out
            == Path(out_path)
            / file.path.parent.parts[-2]
            / file.path.parent.parts[-1]
        )
        assert file_out.is_dir()


class TestFileConv:
    def test_init(self, file_handler):
        _, file_path = file_handler

        # Required only
        file_0 = File(path=file_path)
        file_conv_0 = FileConv(files=[file_0])
        assert file_conv_0.files == [file_0]
        assert file_conv_0.max_errs == int(math.sqrt(len([file_0])))

        # With optional
        file_conv_1 = FileConv(files=[file_0], max_errs=2)
        assert file_conv_1.files == [file_0]
        assert file_conv_1.max_errs == 2
