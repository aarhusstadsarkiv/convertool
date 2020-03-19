from pathlib import Path
from convertool.internals import File, FileConv


class TestFile:
    def test_init(self, file_handler):
        out_path, file_path = file_handler
        file_0 = File(path=file_path, outdir=out_path)
        assert file_0.path == Path(file_path)
        assert file_0.encoding is None
        assert file_0.parent_dirs == 0
        file_1 = File(
            path=file_path, outdir=out_path, encoding=2, parent_dirs=2
        )
        assert file_1.path == Path(file_path)
        assert file_1.encoding == 2
        assert file_1.parent_dirs == 2


class TestFileConv:
    pass
