import csv
from pathlib import Path
from typing import ClassVar

from chardet import DetectionDict
from sas7bdat import SAS7BDAT

from convertool.util import get_encoding
from convertool.util import TempDir

from .base import _shared_dependencies
from .base import _shared_platforms
from .base import _shared_process_timeout
from .base import ConverterABC
from .base import dummy_base_file
from .converter_spreadsheet import ConverterSpreadsheet


class ConverterSAS(ConverterABC):
    tool_names: ClassVar[list[str]] = ["sas"]
    outputs: ClassVar[list[str]] = ["csv", "tsv"]

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


class ConverterSASSpreadsheet(ConverterABC):
    tool_names: ClassVar[list[str]] = ConverterSAS.tool_names
    outputs: ClassVar[list[str]] = ConverterSpreadsheet.outputs
    platforms: ClassVar[list[str]] = _shared_platforms(ConverterSAS, ConverterSpreadsheet)
    dependencies: ClassVar[dict[str, list[str]] | None] = _shared_dependencies(ConverterSAS, ConverterSpreadsheet)
    process_timeout: ClassVar[float | None] = _shared_process_timeout(ConverterSAS, ConverterSpreadsheet)

    def output_puid(self, output: str) -> str | None:
        return ConverterSpreadsheet(self.file, self.root, self.relative_root, self.database).output_puid(output)

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        sas_converter = ConverterSAS(
            self.file,
            self.root,
            self.relative_root,
            self.database,
            timeout=self.timeout,
            capture_output=self.capture_output,
            hashed_output_name=False,
        )

        with TempDir(output_dir) as tmp_dir:
            tmp_file: Path = sas_converter.convert(tmp_dir, "csv", keep_relative_path=keep_relative_path)[0]

            return ConverterSpreadsheet(
                dummy_base_file(tmp_file, tmp_dir),
                tmp_dir,
                tmp_dir,
                self.database,
                timeout=self.timeout,
                capture_output=self.capture_output,
                hashed_output_name=self.hashed_output_name,
            ).convert(
                output_dir,
                output,
                keep_relative_path=keep_relative_path,
            )
