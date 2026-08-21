from pathlib import Path

from acacore.siegfried import Siegfried

from convertool.converters import IPYNBConverter
from convertool.converters.base import dummy_base_file


def test_ipynb_to_html(test_files: dict[str, Path], output_dir: Path, siegfried: Siegfried):
    file = dummy_base_file(test_files["ipynb.ipynb"], test_files["ipynb.ipynb"].parent)
    converter = IPYNBConverter(file, test_files["ipynb.ipynb"].parent)

    output_files = converter.converter(output_dir, "html")
    assert len(output_files) == 1
    assert output_files[0].suffix == ".html"
    assert siegfried.identify(output_files[0]).files[0].best_match().mime == "text/html"
