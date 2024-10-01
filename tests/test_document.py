from os import environ
from pathlib import Path

from acacore.models.file import File
from acacore.siegfried import Siegfried

from convertool.converters.converter_document import ConverterDocument


# noinspection DuplicatedCode
def test_document_to_odt(test_files: dict[str, Path], output_dir: Path):
    for path in [f for n, f in test_files.items() if n.startswith("document.")]:
        print(path.name)

        file = File.from_file(path, root=path.parent)
        converter = ConverterDocument(file)
        siegfried = Siegfried(environ["SIEGFRIED_PATH"], "default.sig", environ["SIEGFRIED_HOME"])

        output_files = converter.convert(output_dir, "odt")
        expected_output_file = file.relative_path.with_suffix(".odt")
        assert len(output_files) == 1
        assert expected_output_file.name in [f.name for f in output_files]
        sf_match = siegfried.identify(output_dir / expected_output_file.name).files[0].best_match()
        assert sf_match and sf_match.mime == "application/vnd.oasis.opendocument.text"


# noinspection DuplicatedCode
def test_document_to_pdf(test_files: dict[str, Path], output_dir: Path):
    for path in [f for n, f in test_files.items() if n.startswith("document.")]:
        print(path.name)

        file = File.from_file(path, root=path.parent)
        converter = ConverterDocument(file)
        siegfried = Siegfried(environ["SIEGFRIED_PATH"], "default.sig", environ["SIEGFRIED_HOME"])

        output_files = converter.convert(output_dir, "pdf")
        expected_output_file = file.relative_path.with_suffix(".pdf")
        assert len(output_files) == 1
        assert expected_output_file.name in [f.name for f in output_files]
        sf_match = siegfried.identify(output_dir / expected_output_file.name).files[0].best_match()
        assert sf_match and sf_match.mime == "application/pdf"


# noinspection DuplicatedCode
def test_document_to_html(test_files: dict[str, Path], output_dir: Path):
    for path in [f for n, f in test_files.items() if n.startswith("document.")]:
        print(path.name)

        file = File.from_file(path, root=path.parent)
        converter = ConverterDocument(file)
        siegfried = Siegfried(environ["SIEGFRIED_PATH"], "default.sig", environ["SIEGFRIED_HOME"])

        output_files = converter.convert(output_dir, "html")
        expected_output_file = file.relative_path.with_suffix(".html")
        assert len(output_files) == 1
        assert expected_output_file.name in [f.name for f in output_files]
        sf_match = siegfried.identify(output_dir / expected_output_file.name).files[0].best_match()
        assert sf_match and sf_match.mime == "text/html"
