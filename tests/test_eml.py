from pathlib import Path

from acacore.siegfried import Siegfried

from convertool.converters import ConverterEML
from convertool.converters import ConverterEMLToImage
from convertool.converters import ConverterEMLToPDF
from convertool.converters.base import dummy_base_file

from .test_image import MIMETYPES


# noinspection DuplicatedCode
def test_eml(test_files: dict[str, Path], reference_files: dict[str, Path], output_dir: Path):
    file = dummy_base_file(test_files["email.eml"], test_files["email.eml"].parent)
    converter = ConverterEML(file, hashed_output_name=False)

    for output in converter.outputs:
        print(output)
        output_files = converter.convert(output_dir, output)
        assert len(output_files) == 1
        assert output_files[0].name in reference_files
        assert reference_files[output_files[0].name].read_text() == output_files[0].read_text()


def test_eml_to_pdf(test_files: dict[str, Path], output_dir: Path, siegfried: Siegfried):
    file = dummy_base_file(test_files["email.eml"], test_files["email.eml"].parent)
    converter = ConverterEMLToPDF(file, hashed_output_name=False)

    output_files = converter.convert(output_dir, "pdf")
    assert len(output_files) == 1
    assert output_files[0].suffix == ".pdf"
    assert siegfried.identify(output_files[0]).files[0].best_match().mime == "application/pdf"


def test_eml_to_image(test_files: dict[str, Path], output_dir: Path, siegfried: Siegfried):
    file = dummy_base_file(test_files["email.eml"], test_files["email.eml"].parent)
    converter = ConverterEMLToImage(file, hashed_output_name=False)

    for output in converter.outputs:
        if output == "jp2":
            continue
        print(output)
        output_files = converter.convert(output_dir, output)
        assert len(output_files) >= 1
        assert all(sf.best_match().mime == MIMETYPES[output] for sf in siegfried.identify(*output_files).files)
