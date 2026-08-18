from pathlib import Path

from convertool.converters import MedComConverter
from convertool.converters import XSLConverter
from convertool.converters.base import dummy_base_file


def test_xml_to_html(test_files: dict[str, Path], reference_files: dict[str, Path], output_dir: Path):
    file = dummy_base_file(test_files["medcom.xml"], test_files["medcom.xml"].parent)
    converter = XSLConverter(file, test_files["medcom.xml"].parent, hashed_output_name=False)

    output_files = converter.convert(output_dir, "html")
    assert len(output_files) == 1
    assert output_files[0].is_file()
    assert output_files[0].name in reference_files
    assert output_files[0].read_text() == reference_files[output_files[0].name].read_text()


def test_medcom_to_html(test_files: dict[str, Path], reference_files: dict[str, Path], output_dir: Path):
    file = dummy_base_file(test_files["medcom.xml"], test_files["medcom.xml"].parent)
    converter = MedComConverter(file, test_files["medcom.xml"].parent, hashed_output_name=False)

    output_files = converter.convert(output_dir, "html")
    assert len(output_files) == 1
    assert output_files[0].is_file()
    assert output_files[0].name in reference_files
    assert output_files[0].read_text() == reference_files[output_files[0].name].read_text()
