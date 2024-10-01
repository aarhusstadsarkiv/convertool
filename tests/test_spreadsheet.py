from os import environ
from pathlib import Path

from acacore.models.file import File
from acacore.siegfried import Siegfried

from convertool.converters.converter_spreadsheet import ConverterSpreadsheet


# noinspection DuplicatedCode
def test_spreadsheet_to_ods(test_files: dict[str, Path], output_dir: Path):
    for path in [f for n, f in test_files.items() if n.startswith("spreadsheet.")]:
        print(path.name)

        file = File.from_file(path, root=path.parent)
        converter = ConverterSpreadsheet(file)
        siegfried = Siegfried(environ["SIEGFRIED_PATH"], "default.sig", environ["SIEGFRIED_HOME"])

        output_files = converter.convert(output_dir, "ods")
        expected_output_file = file.relative_path.with_suffix(".ods")
        assert len(output_files) == 1
        assert expected_output_file.name in [f.name for f in output_files]
        sf_match = siegfried.identify(output_dir / expected_output_file.name).files[0].best_match()
        assert sf_match and sf_match.mime == "application/vnd.oasis.opendocument.spreadsheet"


# noinspection DuplicatedCode
def test_spreadsheet_to_pdf(test_files: dict[str, Path], output_dir: Path):
    for path in [f for n, f in test_files.items() if n.startswith("spreadsheet.")]:
        print(path.name)

        file = File.from_file(path, root=path.parent)
        converter = ConverterSpreadsheet(file)
        siegfried = Siegfried(environ["SIEGFRIED_PATH"], "default.sig", environ["SIEGFRIED_HOME"])

        output_files = converter.convert(output_dir, "pdf")
        expected_output_file = file.relative_path.with_suffix(".pdf")
        assert len(output_files) == 1
        assert expected_output_file.name in [f.name for f in output_files]
        sf_match = siegfried.identify(output_dir / expected_output_file.name).files[0].best_match()
        assert sf_match and sf_match.mime == "application/pdf"


# noinspection DuplicatedCode
def test_spreadsheet_to_html(test_files: dict[str, Path], output_dir: Path):
    for path in [f for n, f in test_files.items() if n.startswith("spreadsheet.")]:
        print(path.name)

        file = File.from_file(path, root=path.parent)
        converter = ConverterSpreadsheet(file)
        siegfried = Siegfried(environ["SIEGFRIED_PATH"], "default.sig", environ["SIEGFRIED_HOME"])

        output_files = converter.convert(output_dir, "html")
        expected_output_file = file.relative_path.with_suffix(".html")
        assert len(output_files) == 1
        assert expected_output_file.name in [f.name for f in output_files]
        sf_match = siegfried.identify(output_dir / expected_output_file.name).files[0].best_match()
        assert sf_match and sf_match.mime == "text/html"
