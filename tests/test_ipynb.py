from pathlib import Path

from acacore.siegfried import Siegfried
from converters import ConverterIPYNBToHTML
from converters import ConverterIPYNBToImage
from converters import ConverterIPYNBToPDF

from convertool.converters.base import dummy_base_file

from .test_image import MIMETYPES


def test_ipynb_to_html(test_files: dict[str, Path], output_dir: Path, siegfried: Siegfried):
    file = dummy_base_file(test_files["ipynb.ipynb"], test_files["ipynb.ipynb"].parent)
    converter = ConverterIPYNBToHTML(file)

    output_files = converter.convert(output_dir, "html")
    assert len(output_files) == 1
    assert output_files[0].suffix == ".html"
    assert siegfried.identify(output_files[0]).files[0].best_match().mime == "text/html"


def test_ipynb_to_pdf(test_files: dict[str, Path], output_dir: Path, siegfried: Siegfried):
    file = dummy_base_file(test_files["ipynb.ipynb"], test_files["ipynb.ipynb"].parent)
    converter = ConverterIPYNBToPDF(file)

    output_files = converter.convert(output_dir, "pdf")
    assert len(output_files) == 1
    assert output_files[0].suffix == ".pdf"
    assert siegfried.identify(output_files[0]).files[0].best_match().mime == "application/pdf"


def test_ipynb_to_image(test_files: dict[str, Path], output_dir: Path, siegfried: Siegfried):
    file = dummy_base_file(test_files["ipynb.ipynb"], test_files["ipynb.ipynb"].parent)
    converter = ConverterIPYNBToImage(file)

    for output in converter.outputs:
        print(output)
        output_files = converter.convert(output_dir, output)
        assert len(output_files) >= 1
        mimes = {sf.best_match().mime for sf in siegfried.identify(*output_files).files}
        assert mimes == {MIMETYPES[output]}, output
