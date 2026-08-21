from pathlib import Path

from acacore.database import FilesDB

from convertool.converters import GISConverter
from convertool.converters.base import dummy_base_file
from convertool.util import AVID


# noinspection DuplicatedCode
def test_gis_to_gml(test_files: dict[str, Path], reference_files: dict[str, Path], output_dir: Path):
    file = dummy_base_file(test_files["gis.tab"], test_files["gis.tab"].parent)
    converter = GISConverter(file, test_files["gis.tab"].parent, hashed_output_name=False)

    output_files = converter.converter(output_dir, "gml")
    assert len(output_files) == 2
    assert all(of.name in reference_files for of in output_files)
    for of in output_files:
        assert of.read_bytes() == reference_files[of.name].read_bytes()


def test_gis_to_gml_database(avid_dir_copy: Path, output_dir: Path):
    avid = AVID(avid_dir_copy)

    with FilesDB(avid.database_path) as db:
        for file in db.original_files.select("gis_main is not null and action = 'convert'"):
            converter = GISConverter(file, avid.path, avid.dirs.original_documents, db, hashed_output_name=False)
            output_files = converter.converter(output_dir, "gml")
            assert len(output_files) == 2
