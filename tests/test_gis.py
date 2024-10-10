from pathlib import Path
from wsgiref.validate import assert_

from acacore.models.file import File

from convertool.converters import ConverterMSG


# noinspection DuplicatedCode
def test_gis_to_gml(test_files: dict[str, Path], reference_files: dict[str, Path], output_dir: Path):
    file = File.from_file(test_files["gis.tab"], root=test_files["gis.tab"].parent)
    converter = ConverterMSG(file)

    output_files = converter.convert(output_dir, "gml")
    assert len(output_files) == 2
    assert all(of.name in reference_files for of in output_files)
    assert all(of.read_text() == reference_files[of.name].read_text() for of in output_files)
