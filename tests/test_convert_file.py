from pathlib import Path

import structlog

from convertool.convert import convert_file
from convertool.converters import converters
from convertool.converters import ConvertersGraph


def test_convert_file_graph(test_files: dict[str, Path], output_dir: Path):
    file = test_files["medcom.xml"]
    logger = structlog.stdlib.get_logger()

    outputs = convert_file(
        "test",
        file,
        file.parent,
        output_dir,
        (ConvertersGraph.from_conversers(converters), "medcom", "pdf", None),
        None,
        logger,
    )

    assert len(outputs) == 1
    assert outputs[0].name == file.with_suffix(".pdf").name
