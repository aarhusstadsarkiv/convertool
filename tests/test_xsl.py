from pathlib import Path

from acacore.models.file import BaseFile
from acacore.siegfried import Siegfried

from convertool.converters import ConverterXSL
from convertool.converters import ConverterXSLToImage
from convertool.converters import ConverterXSLToPDF

from .test_image import MIMETYPES


def test_xml_to_html(test_files: dict[str, Path], reference_files: dict[str, Path], output_dir: Path):
    file = BaseFile.from_file(test_files["medcom.xml"], root=test_files["medcom.xml"].parent)
    converter = ConverterXSL(file)

    output_files = converter.convert(output_dir, "html")
    assert len(output_files) == 1
    assert output_files[0].is_file()
    assert output_files[0].name in reference_files
    assert output_files[0].read_text() == reference_files[output_files[0].name].read_text()


def test_xml_to_pdf(test_files: dict[str, Path], output_dir: Path, siegfried: Siegfried):
    file = BaseFile.from_file(test_files["medcom.xml"], root=test_files["medcom.xml"].parent)
    converter = ConverterXSLToPDF(file)

    output_files = converter.convert(output_dir, "pdf")
    assert len(output_files) == 1
    assert output_files[0].is_file()
    match = siegfried.identify(output_files[0]).files[0]
    assert match.best_match().mime == "application/pdf"


def test_xml_to_image(test_files: dict[str, Path], output_dir: Path, siegfried: Siegfried):
    file = BaseFile.from_file(test_files["medcom.xml"], root=test_files["medcom.xml"].parent)
    converter = ConverterXSLToImage(file)

    for output in converter.outputs:
        output_files = converter.convert(output_dir, output)
        assert len(output_files) > 1
        assert all(f.is_file() for f in output_files)
        assert all(f.best_match().mime == MIMETYPES[output] for f in siegfried.identify(*output_files).files)
