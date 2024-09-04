from pathlib import Path

from acacore.models.file import File

from convertool.converters.converter_to_img import ConverterTextToImg


def test_text_to_img(test_files: dict[str, Path], reference_files: dict[str, Path], output_dir: Path):
    file = File.from_file(test_files["text_to_img.txt"], root=test_files["text_to_img.txt"].parent)
    converter = ConverterTextToImg(file)

    for output in converter.outputs:
        print(output)
        output_files = converter.convert(output_dir, output)
        assert len(output_files) == 1
        assert output_files[0].name in reference_files
        assert reference_files[output_files[0].name].stat().st_size == output_files[0].stat().st_size
