from pathlib import Path
from sys import stderr
from typing import ClassVar

from convertool.util import TempDir

from .base import _dummy_base_file
from .base import _shared_dependencies
from .base import _shared_platforms
from .base import _shared_process_timeout
from .base import ConverterABC
from .converter_image import ConverterImage
from .exceptions import ConvertError


class ConverterMDI(ConverterABC):
    tool_names: ClassVar[list[str]] = ["mdi"]
    outputs: ClassVar[list[str]] = ["tif", "tiff"]
    process_timeout: ClassVar[float] = 120
    platforms: ClassVar[list[str]] = ["win32"]
    dependencies: ClassVar[dict[str, list[str]]] = {"mdi2tif": ["mdi2tif"]}

    def output(self, output: str) -> str:
        if output == "tiff":
            output = "tif"
        return super().output(output)

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = self.output_file(dest_dir, output)

        with TempDir(output_dir) as tmp_dir:
            tmp_file: Path = tmp_dir.joinpath(dest_file.name)
            tmp_log: Path = tmp_dir.joinpath("log.txt")
            self.run_process(
                self.dependencies["mdi2tif"][0],
                "--source",
                self.file.get_absolute_path(),
                "--dest",
                tmp_file,
                "--log",
                tmp_log,
            )

            if not self.capture_output and tmp_log.is_file() and (log := tmp_log.read_text().strip()):
                print(log, file=stderr)

            if tmp_file.is_file():
                dest_dir.mkdir(parents=True, exist_ok=True)
                return [tmp_file.replace(dest_file)]

            raise ConvertError(self.file, "Could not convert file.")


class ConverterMDIToPDF(ConverterABC):
    tool_names: ClassVar[list[str]] = ["mdi"]
    outputs: ClassVar[list[str]] = ["pdf"]
    process_timeout: ClassVar[float] = _shared_process_timeout(ConverterMDI, ConverterImage)
    platforms: ClassVar[list[str]] = _shared_platforms(ConverterMDI, ConverterImage)
    dependencies: ClassVar[dict[str, list[str]]] = _shared_dependencies(ConverterMDI, ConverterImage)

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = self.output_file(dest_dir, output)

        with TempDir(output_dir) as tmp_dir:
            tiff: Path = ConverterMDI(
                self.file, self.database, self.file.root, capture_output=self.capture_output
            ).convert(tmp_dir, "tif", keep_relative_path=False)[0]
            pdfs: list[Path] = ConverterImage(
                _dummy_base_file(tiff, tmp_dir),
                None,
                tmp_dir,
                capture_output=self.capture_output,
            ).convert(tmp_dir, output, keep_relative_path=False)

            if pdfs:
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                return [pdfs[0].replace(dest_file)]

        raise ConvertError(self.file, "Could not convert file.")
