from pathlib import Path

from acacore.models.file import File
from acacore.siegfried import Siegfried

from convertool.converters.converter_image import ConverterImage
from convertool.converters.converter_image import ConverterPDFToImage
from convertool.converters.converter_image import ConverterTextToImage

MIMETYPES = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "tif": "image/tiff",
    "tiff": "image/tiff",
    "jp2": "image/jp2",
    "pdf": "application/pdf",
}


# noinspection DuplicatedCode
def test_img_to_img(test_files: dict[str, Path], output_dir: Path, siegfried: Siegfried):
    file = File.from_file(test_files["img-to-img.webp"], root=test_files["img-to-img.webp"].parent)
    converter = ConverterImage(file)

    for output in converter.outputs:
        print(output)
        output_files = converter.convert(output_dir, output)
        assert len(output_files) == 1
        assert siegfried.identify(output_files[0]).files[0].best_match().mime == MIMETYPES[output]


# noinspection DuplicatedCode
def test_pdf_to_img(test_files: dict[str, Path], output_dir: Path, siegfried: Siegfried):
    file = File.from_file(test_files["pdf-to-img.pdf"], root=test_files["pdf-to-img.pdf"].parent)
    converter = ConverterPDFToImage(file)

    for output in converter.outputs:
        print(output)
        output_files = converter.convert(output_dir, output)
        assert len(output_files) >= 1
        assert all(sf.best_match().mime == MIMETYPES[output] for sf in siegfried.identify(*output_files).files)


# noinspection DuplicatedCode
def test_text_to_img(test_files: dict[str, Path], output_dir: Path, siegfried: Siegfried):
    file = File.from_file(test_files["text_to_img.txt"], root=test_files["text_to_img.txt"].parent)
    converter = ConverterTextToImage(file)

    for output in converter.outputs:
        print(output)
        output_files = converter.convert(output_dir, output)
        assert len(output_files) == 1
        assert all(sf.best_match().mime == MIMETYPES[output] for sf in siegfried.identify(*output_files).files)
