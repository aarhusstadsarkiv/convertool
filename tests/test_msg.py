from pathlib import Path

from acacore.models.file import File
from acacore.siegfried import Siegfried

from convertool.converters import ConverterMSG
from convertool.converters import ConverterMSGToImage
from convertool.converters import ConverterMSGToPDF

from .test_image import MIMETYPES


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


def test_msg_to_pdf(test_files: dict[str, Path], output_dir: Path, siegfried: Siegfried):
    file = File.from_file(test_files["message.msg"], root=test_files["message.msg"].parent)
    converter = ConverterMSGToPDF(file)

    output_files = converter.convert(output_dir, "pdf")
    assert len(output_files) == 1
    assert output_files[0].suffix == ".pdf"
    assert siegfried.identify(output_files[0]).files[0].best_match().mime == "application/pdf"


def test_msg_to_image(test_files: dict[str, Path], output_dir: Path, siegfried: Siegfried):
    file = File.from_file(test_files["message.msg"], root=test_files["message.msg"].parent)
    converter = ConverterMSGToImage(file)

    for output in converter.outputs:
        print(output)
        output_files = converter.convert(output_dir, output)
        assert len(output_files) >= 1
        assert all(sf.best_match().mime == MIMETYPES[output] for sf in siegfried.identify(*output_files).files)
