from pathlib import Path

from convertool.converters.base import dummy_base_file
from convertool.converters.converter_tnef import ConverterTNEF


# noinspection DuplicatedCode
def test_tnef(test_files: dict[str, Path], reference_files: dict[str, Path], output_dir: Path):
    file = dummy_base_file(test_files["winmail.dat"], test_files["winmail.dat"].parent)
    converter = ConverterTNEF(file)

    for output in converter.outputs:
        print(output)
        output_files = converter.convert(output_dir, output)
        assert len(output_files) == 1
        assert output_files[0].name in reference_files
        assert reference_files[output_files[0].name].read_text() == output_files[0].read_text()
