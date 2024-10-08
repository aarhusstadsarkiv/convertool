from pathlib import Path

from acacore.models.file import File

from convertool.converters import ConverterMSG


# noinspection DuplicatedCode
def test_msg(test_files: dict[str, Path], reference_files: dict[str, Path], output_dir: Path):
    file = File.from_file(test_files["message.msg"], root=test_files["message.msg"].parent)
    converter = ConverterMSG(file)

    for output in converter.outputs:
        print(output)
        output_files = converter.convert(output_dir, output)
        assert len(output_files) == 1
        assert output_files[0].name in reference_files
        assert reference_files[output_files[0].name].read_text() == output_files[0].read_text()
