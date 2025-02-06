import csv
from pathlib import Path
from typing import ClassVar

from sas7bdat import SAS7BDAT

from convertool.util import get_encoding
from convertool.util import TempDir

from .base import ConverterABC


class ConverterSAS(ConverterABC):
    tool_names: ClassVar[list[str]] = ["sas"]
    outputs: ClassVar[list[str]] = ["csv", "tsv"]

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = self.output_file(dest_dir, output)

        encoding: str | None = get_encoding(self.file.get_absolute_path())

        delimiter: str = ","

        if output == "tsv":
            delimiter = "\t"

        with (
            TempDir(output_dir) as tmp_dir,
            SAS7BDAT(str(self.file.get_absolute_path()), encoding=encoding or "utf-8") as sas_file,
        ):
            tmp_file: Path = tmp_dir.joinpath("sas")

            with tmp_file.open("w", encoding="utf-8") as fh:
                writer = csv.writer(fh, delimiter=delimiter)
                for row in sas_file:
                    writer.writerow(row)

            dest_dir.mkdir(parents=True, exist_ok=True)
            tmp_file.replace(dest_file)

        return [dest_file]
