from pathlib import Path

from acacore.siegfried import Siegfried

from convertool.converters.base import dummy_base_file
from convertool.converters.base import hashed_file_name
from convertool.converters.converter_document import DocumentConverter


# noinspection DuplicatedCode
def test_document_to_odt(test_files: dict[str, Path], output_dir: Path, siegfried: Siegfried):
    for path in [f for n, f in test_files.items() if n.startswith("document.")]:
        print(path.name)

        file = dummy_base_file(path, path.parent)
        converter = DocumentConverter(file, path.parent, hashed_output_name=True)

        output_files = converter.converter(output_dir, "odt")
        expected_output_file = hashed_file_name(file.relative_path / file.relative_path.with_suffix(".odt").name)
        assert len(output_files) == 1
        assert expected_output_file in [f.name for f in output_files]
        sf_match = siegfried.identify(output_dir / expected_output_file).files[0].best_match()
        assert sf_match is not None
        assert sf_match.mime == "application/vnd.oasis.opendocument.text"


# noinspection DuplicatedCode
def test_document_to_pdf(test_files: dict[str, Path], output_dir: Path, siegfried: Siegfried):
    for path in [f for n, f in test_files.items() if n.startswith("document.")]:
        print(path.name)

        file = dummy_base_file(path, path.parent)
        converter = DocumentConverter(file, path.parent, hashed_output_name=True)

        output_files = converter.converter(output_dir, "pdf")
        expected_output_file = hashed_file_name(file.relative_path / file.relative_path.with_suffix(".pdf").name)
        assert len(output_files) == 1
        assert expected_output_file in [f.name for f in output_files]
        sf_match = siegfried.identify(output_dir / expected_output_file).files[0].best_match()
        assert sf_match is not None
        assert sf_match.mime == "application/pdf"


# noinspection DuplicatedCode
def test_document_to_html(test_files: dict[str, Path], output_dir: Path, siegfried: Siegfried):
    for path in [f for n, f in test_files.items() if n.startswith("document.")]:
        print(path.name)

        file = dummy_base_file(path, path.parent)
        converter = DocumentConverter(file, path.parent, hashed_output_name=True)

        output_files = converter.converter(output_dir, "html")
        expected_output_file = hashed_file_name(file.relative_path / file.relative_path.with_suffix(".html").name)
        assert len(output_files) == 1
        assert expected_output_file in [f.name for f in output_files]
        sf_match = siegfried.identify(output_dir / expected_output_file).files[0].best_match()
        assert sf_match is not None
        assert sf_match.mime == "text/html"
