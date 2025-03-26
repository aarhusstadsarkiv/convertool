from pathlib import Path

import pytest
from acacore.models.file import BaseFile

from convertool.converters import ConverterZIPFile
from convertool.converters.exceptions import BadOption


def test_zipfile(test_files: dict[str, Path], test_files_dir: Path, output_dir: Path):
    file = BaseFile.from_file(test_files["presentation.pptx"], root=test_files_dir)
    converter = ConverterZIPFile(file, options={"path": "ppt/media/image1.jpeg"})

    output_files = converter.convert(output_dir, "")
    assert len(output_files) == 1
    assert output_files[0].is_file()
    assert output_files[0].name == file.relative_path.with_suffix(Path(converter.options["path"]).suffix).name


def test_zipfile_errors():
    file = BaseFile.from_file(__file__, "/")

    with pytest.raises(BadOption):
        ConverterZIPFile(file, options=None)
