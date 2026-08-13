from pathlib import Path

from converters import ConvertersEdge
from converters import MedComConverter

from convertool.converters import ConvertersPath
from convertool.converters import dummy_base_file
from convertool.converters import HTMLConverter


def test_converter_path(test_files: dict[str, Path], output_dir: Path):
    path = ConvertersPath(
        MedComConverter.name,
        HTMLConverter.outputs[0],
        [
            ConvertersEdge(MedComConverter, HTMLConverter.name),
            ConvertersEdge(HTMLConverter, HTMLConverter.outputs[0]),
        ],
    )

    path.test()

    file = dummy_base_file(test_files["medcom.xml"], test_files["medcom.xml"].parent)

    files, convs = path(file, test_files["medcom.xml"].parent, output_dir, test_files["medcom.xml"].parent, None)

    assert len(files) == 1
    assert len(convs) == 2
    assert isinstance(convs[0][0], ConvertersEdge)
    assert isinstance(convs[0][1], MedComConverter)
    assert isinstance(convs[1][0], ConvertersEdge)
    assert isinstance(convs[1][1], HTMLConverter)
    assert files[0].name == test_files["medcom.xml"].with_suffix(convs[1][1].output_extension(HTMLConverter.outputs[0]))
