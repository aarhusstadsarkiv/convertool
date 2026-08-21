from pathlib import Path

from convertool.converters import EMLConverter
from convertool.converters.base import dummy_base_file


# noinspection DuplicatedCode
def test_eml(test_files: dict[str, Path], reference_files: dict[str, Path], output_dir: Path):
    file = dummy_base_file(test_files["email.eml"], test_files["email.eml"].parent)
    converter = EMLConverter(file, test_files["email.eml"].parent, hashed_output_name=False)

    for output in converter.outputs:
        print(output)
        output_files = converter.converter(output_dir, output)
        assert len(output_files) == 1
        assert output_files[0].name in reference_files
        assert reference_files[output_files[0].name].read_text() == output_files[0].read_text()
