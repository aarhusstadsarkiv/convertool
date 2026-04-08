from pathlib import Path

from acacore.siegfried import Siegfried

from convertool.converters.base import dummy_base_file
from convertool.converters.converter_text import ConverterTextToImage

from .test_image import MIMETYPES


# noinspection DuplicatedCode
def test_text_to_img(test_files: dict[str, Path], output_dir: Path, siegfried: Siegfried):
    file = dummy_base_file(test_files["text_to_img.txt"], test_files["text_to_img.txt"].parent)
    converter = ConverterTextToImage(file)

    for output in converter.outputs:
        print(output)
        output_files = converter.convert(output_dir, output)
        assert len(output_files) == 1
        assert all(sf.best_match().mime == MIMETYPES[output] for sf in siegfried.identify(*output_files).files)
