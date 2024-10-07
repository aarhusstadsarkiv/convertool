from pathlib import Path

from acacore.models.file import File
from acacore.siegfried import Siegfried

from convertool.converters.converter_presentation import ConverterPresentation


# noinspection DuplicatedCode
def test_presentation_to_odp(test_files: dict[str, Path], output_dir: Path, siegfried: Siegfried):
    for path in [f for n, f in test_files.items() if n.startswith("presentation.")]:
        print(path.name)

        file = File.from_file(path, root=path.parent)
        converter = ConverterPresentation(file)

        output_files = converter.convert(output_dir, "odp")
        expected_output_file = file.relative_path.with_suffix(".odp")
        assert len(output_files) == 1
        assert expected_output_file.name in [f.name for f in output_files]
        sf_match = siegfried.identify(output_dir / expected_output_file.name).files[0].best_match()
        assert sf_match and sf_match.mime == "application/vnd.oasis.opendocument.presentation"


# noinspection DuplicatedCode
def test_presentation_to_pdf(test_files: dict[str, Path], output_dir: Path, siegfried: Siegfried):
    for path in [f for n, f in test_files.items() if n.startswith("presentation.")]:
        print(path.name)

        file = File.from_file(path, root=path.parent)
        converter = ConverterPresentation(file)

        output_files = converter.convert(output_dir, "pdf")
        expected_output_file = file.relative_path.with_suffix(".pdf")
        assert len(output_files) == 1
        assert expected_output_file.name in [f.name for f in output_files]
        sf_match = siegfried.identify(output_dir / expected_output_file.name).files[0].best_match()
        assert sf_match and sf_match.mime == "application/pdf"


# noinspection DuplicatedCode
def test_presentation_to_html(test_files: dict[str, Path], output_dir: Path, siegfried: Siegfried):
    for path in [f for n, f in test_files.items() if n.startswith("presentation.")]:
        print(path.name)

        file = File.from_file(path, root=path.parent)
        converter = ConverterPresentation(file)

        output_files = converter.convert(output_dir, "html")
        expected_output_file = file.relative_path.with_suffix(".html")
        assert len(output_files) == 1
        assert expected_output_file.name in [f.name for f in output_files]
        sf_match = siegfried.identify(output_dir / expected_output_file.name).files[0].best_match()
        assert sf_match and sf_match.mime in ("text/html", "application/xml")
