from pathlib import Path

import pytest

from convertool.converters import ConverterZIPFile
from convertool.converters.base import dummy_base_file
from convertool.converters.exceptions import BadOption


def test_zipfile(test_files: dict[str, Path], test_files_dir: Path, output_dir: Path):
    file = dummy_base_file(test_files["presentation.pptx"], test_files_dir)
    converter = ConverterZIPFile(file, options={"path": "ppt/media/image1.jpeg"})

    output_files = converter.convert(output_dir, "")
    assert len(output_files) == 1
    assert output_files[0].is_file()
    assert output_files[0].name == file.relative_path.with_suffix(Path(converter.options["path"]).suffix).name


def test_zipfile_errors():
    file = dummy_base_file(__file__, Path("/"))

    with pytest.raises(BadOption):
        ConverterZIPFile(file, options=None)
