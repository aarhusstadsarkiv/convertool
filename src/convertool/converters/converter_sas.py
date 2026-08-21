import csv
from pathlib import Path
from typing import ClassVar

from chardet import DetectionDict
from sas7bdat import SAS7BDAT

from convertool.util import get_encoding
from convertool.util import TempDir

from .base import ConverterABC


class SASConverter(ConverterABC):
    name: ClassVar[str] = "sas"
    outputs: ClassVar[list[str]] = ["csv", "tsv"]

    @classmethod
    def output_name(cls, output: str) -> str:
        return "spreadsheet"

    def output_extension(self, output: str) -> str:
        if output == "csv":
            return ".csv"
        if output == "tsv":
            return ".tsv"
        return super().output_extension(output)

    def output_puid(self, output: str) -> str | None:
        if output == "csv":
            return "x-fmt/18"
        if output == "tsv":
            return "x-fmt/13"
        return None

    def output_encoding(self, output: str) -> DetectionDict | None:
        if output == "csv":
            return DetectionDict(encoding="utf-8", confidence=1.0, language=None, mime_type="text/csv")
        if output == "tsv":
            return DetectionDict(encoding="utf-8", confidence=1.0, language=None, mime_type=None)
        return None

    def converter(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        self.test_output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = dest_dir.joinpath(self.output_filename(output))

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
