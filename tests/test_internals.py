import math
from pathlib import Path

from pydantic import ValidationError

import pytest
from convertool.internals import File, FileConv, FileInfo, size_fmt


class TestFileInfo:
    def test_init(self, file_handler):
        _, file_path = file_handler
        file_info = FileInfo(path=file_path)
        file_path = Path(file_path)
        assert file_info.path == file_path
        assert file_info.name == file_path.name
        assert file_info.ext == file_path.suffix.lower()
        assert file_info.size == size_fmt(file_path.stat().st_size)

    def test_validators(self, file_handler, capsys):
        with pytest.raises(ValidationError, match="File does not exist"):
            FileInfo(path="test", name="test", ext="test", size="test")
        captured = capsys.readouterr()
        assert "Warning! name=test will be overwritten" in captured.out
        assert "Warning! ext=test will be overwritten" in captured.out
        assert "Warning! size=test will be overwritten" in captured.out


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
