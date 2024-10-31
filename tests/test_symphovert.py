from pathlib import Path

import pytest
from acacore.models.file import File

from convertool.converters import ConverterSymphovert
from convertool.converters.exceptions import ConvertError


# noinspection DuplicatedCode
def test_symphovert(test_files: dict[str, Path], output_dir: Path):
    file = File.from_file(test_files["document.docx"], root=test_files["document.docx"].parent)
    converter = ConverterSymphovert(file)

    for output in converter.outputs:
        expected_file = output_dir.joinpath(file.name).with_suffix(f".{output}")
        expected_file.write_text("")
        output_files = converter.convert(output_dir, output)
        assert len(output_files) == 1
        assert output_files[0] == expected_file

    with pytest.raises(ConvertError, match="not found"):
        output_dir.joinpath(file.name).with_suffix(".odt").unlink(missing_ok=True)
        ConverterSymphovert(file).convert(output_dir, "odt")
