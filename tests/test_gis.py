from pathlib import Path

from convertool.converters import ConverterGIS
from convertool.converters.base import dummy_base_file


# noinspection DuplicatedCode
def test_gis_to_gml(test_files: dict[str, Path], reference_files: dict[str, Path], output_dir: Path):
    file = dummy_base_file(test_files["gis.tab"], test_files["gis.tab"].parent)
    converter = ConverterGIS(file, hashed_putput_name=False)

    output_files = converter.convert(output_dir, "gml")
    assert len(output_files) == 2
    assert all(of.name in reference_files for of in output_files)
    for of in output_files:
        assert of.read_bytes() == reference_files[of.name].read_bytes()
