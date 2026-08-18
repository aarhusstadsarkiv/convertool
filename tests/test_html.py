from pathlib import Path

from acacore.siegfried import Siegfried

from convertool.converters import HTMLConverter
from convertool.converters.base import dummy_base_file


def test_html_to_pdf(test_files: dict[str, Path], output_dir: Path, siegfried: Siegfried):
    for path in [f for n, f in test_files.items() if n.startswith("html")]:
        file = dummy_base_file(path, path.parent)
        converter = HTMLConverter(file, path.parent)

        output_files = converter.convert(output_dir, "pdf")
        assert len(output_files) == 1
        assert output_files[0].suffix == ".pdf"
        assert siegfried.identify(output_files[0]).files[0].best_match().mime == "application/pdf"
