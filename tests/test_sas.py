from pathlib import Path

from acacore.models.file import BaseFile

from convertool.converters import ConverterSAS


def test_sas_to_csv(test_files: dict[str, Path], output_dir: Path):
    for path in [f for n, f in test_files.items() if n.endswith(".sas7bdat")]:
        file = BaseFile.from_file(path, root=path.parent)
        converter = ConverterSAS(file)

        output_files = converter.convert(output_dir, "csv")
        assert len(output_files) == 1
        assert output_files[0].suffix == ".csv"


def test_sas_to_tsv(test_files: dict[str, Path], output_dir: Path):
    for path in [f for n, f in test_files.items() if n.endswith(".sas7bdat")]:
        file = BaseFile.from_file(path, root=path.parent)
        converter = ConverterSAS(file)

        output_files = converter.convert(output_dir, "tsv")
        assert len(output_files) == 1
        assert output_files[0].suffix == ".tsv"
