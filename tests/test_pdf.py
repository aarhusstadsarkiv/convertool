from pathlib import Path

from acacore.siegfried import Siegfried

from convertool.converters.base import dummy_base_file
from convertool.converters.converter_pdf import ConverterPDF
from convertool.converters.converter_pdf import ConverterPDFToImage

from .test_image import MIMETYPES


# noinspection DuplicatedCode
def test_pdf_to_pdfa(test_files: dict[str, Path], output_dir: Path, siegfried: Siegfried):
    file = dummy_base_file(test_files["pdf-to-pdfa.pdf"], test_files["pdf-to-pdfa.pdf"].parent)
    converter = ConverterPDF(file, test_files["pdf-to-pdfa.pdf"].parent)

    for pdfa_ver in (1, 2, 3):
        output: str = f"pdfa-{pdfa_ver}"
        print(output)
        output_files = converter.convert(output_dir, output)
        assert len(output_files) == 1
        assert output_files[0].is_file()
        match = siegfried.identify(output_files[0]).files[0]
        assert match.best_match().mime == "application/pdf"


# noinspection DuplicatedCode
def test_pdf_to_img(test_files: dict[str, Path], output_dir: Path, siegfried: Siegfried):
    file = dummy_base_file(test_files["pdf-to-img.pdf"], test_files["pdf-to-img.pdf"].parent)
    converter = ConverterPDFToImage(file, test_files["pdf-to-img.pdf"].parent)

    for output in converter.outputs:
        print(output)
        output_files = converter.convert(output_dir, output)
        assert len(output_files) >= 1
        assert all(sf.best_match().mime == MIMETYPES[output] for sf in siegfried.identify(*output_files).files)
