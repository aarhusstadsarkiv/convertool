from pathlib import Path

from acacore.models.file import File

from convertool.converters.converter_to_img import ConverterPDFToImg
from convertool.converters.converter_to_img import ConverterTextToImg
from convertool.converters.converter_to_img import ConverterToImg


# noinspection DuplicatedCode
def test_img_to_img(test_files: dict[str, Path], reference_files: dict[str, Path], output_dir: Path):
    file = File.from_file(test_files["img-to-img.webp"], root=test_files["img-to-img.webp"].parent)
    converter = ConverterToImg(file)

    for output in converter.outputs:
        print(output)
        output_files = converter.convert(output_dir, output)
        assert len(output_files) == 1
        assert output_files[0].name in reference_files
        assert reference_files[output_files[0].name].stat().st_size == output_files[0].stat().st_size


# noinspection DuplicatedCode
def test_pdf_to_img(test_files: dict[str, Path], reference_files: dict[str, Path], output_dir: Path):
    file = File.from_file(test_files["pdf-to-img.pdf"], root=test_files["pdf-to-img.pdf"].parent)
    converter = ConverterPDFToImg(file)

    for output in converter.outputs:
        print(output)
        output_files = converter.convert(output_dir, output)
        assert all(o.name in reference_files for o in output_files)
        assert all(reference_files[o.name].stat().st_size == o.stat().st_size for o in output_files)


# noinspection DuplicatedCode
def test_text_to_img(test_files: dict[str, Path], reference_files: dict[str, Path], output_dir: Path):
    file = File.from_file(test_files["text_to_img.txt"], root=test_files["text_to_img.txt"].parent)
    converter = ConverterTextToImg(file)

    for output in converter.outputs:
        print(output)
        output_files = converter.convert(output_dir, output)
        assert len(output_files) == 1
        assert output_files[0].name in reference_files
        assert reference_files[output_files[0].name].stat().st_size == output_files[0].stat().st_size
