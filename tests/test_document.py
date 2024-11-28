from pathlib import Path

from acacore.models.file import BaseFile
from acacore.siegfried import Siegfried

from convertool.converters.converter_document import ConverterDocument
from convertool.converters.converter_document import ConverterDocumentToImage

from .test_image import MIMETYPES


# noinspection DuplicatedCode
def test_document_to_odt(test_files: dict[str, Path], output_dir: Path, siegfried: Siegfried):
    for path in [f for n, f in test_files.items() if n.startswith("document.")]:
        print(path.name)

        file = BaseFile.from_file(path, root=path.parent)
        converter = ConverterDocument(file)

        output_files = converter.convert(output_dir, "odt")
        expected_output_file = file.relative_path.with_suffix(".odt")
        assert len(output_files) == 1
        assert expected_output_file.name in [f.name for f in output_files]
        sf_match = siegfried.identify(output_dir / expected_output_file.name).files[0].best_match()
        assert sf_match is not None
        assert sf_match.mime == "application/vnd.oasis.opendocument.text"


# noinspection DuplicatedCode
def test_document_to_pdf(test_files: dict[str, Path], output_dir: Path, siegfried: Siegfried):
    for path in [f for n, f in test_files.items() if n.startswith("document.")]:
        print(path.name)

        file = BaseFile.from_file(path, root=path.parent)
        converter = ConverterDocument(file)

        output_files = converter.convert(output_dir, "pdf")
        expected_output_file = file.relative_path.with_suffix(".pdf")
        assert len(output_files) == 1
        assert expected_output_file.name in [f.name for f in output_files]
        sf_match = siegfried.identify(output_dir / expected_output_file.name).files[0].best_match()
        assert sf_match is not None
        assert sf_match.mime == "application/pdf"


# noinspection DuplicatedCode
def test_document_to_html(test_files: dict[str, Path], output_dir: Path, siegfried: Siegfried):
    for path in [f for n, f in test_files.items() if n.startswith("document.")]:
        print(path.name)

        file = BaseFile.from_file(path, root=path.parent)
        converter = ConverterDocument(file)

        output_files = converter.convert(output_dir, "html")
        expected_output_file = file.relative_path.with_suffix(".html")
        assert len(output_files) == 1
        assert expected_output_file.name in [f.name for f in output_files]
        sf_match = siegfried.identify(output_dir / expected_output_file.name).files[0].best_match()
        assert sf_match is not None
        assert sf_match.mime == "text/html"


def test_document_to_img(test_files: dict[str, Path], output_dir: Path, siegfried: Siegfried):
    file = BaseFile.from_file(test_files["document.docx"], root=test_files["document.docx"].parent)
    converter = ConverterDocumentToImage(file)

    for output in converter.outputs:
        print(output)
        output_files = converter.convert(output_dir, output)
        assert len(output_files) >= 1
        assert all(sf.best_match().mime == MIMETYPES[output] for sf in siegfried.identify(*output_files).files)
