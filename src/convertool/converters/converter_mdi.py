from pathlib import Path
from sys import stderr
from typing import ClassVar

from convertool.util import TempDir

from .base import ConverterABC
from .exceptions import ConvertError


class MDIConverter(ConverterABC):
    name: ClassVar[str] = "mdi"
    outputs: ClassVar[list[str]] = ["tiff"]
    process_timeout: ClassVar[int] = 120
    platforms: ClassVar[list[str]] = ["win32"]
    dependencies: ClassVar[dict[str, list[str]]] = {"mdi2tif": ["mdi2tif"]}

    @classmethod
    def output_name(cls, output: str) -> str:
        return "image"

    def output_extension(self, output: str) -> str:
        return ".tif"

    def output_puid(self, output: str) -> str | None:
        return "fmt/353"

    def converter(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        self.test_output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = dest_dir.joinpath(self.output_filename(output))

        with TempDir(output_dir) as tmp_dir:
            tmp_file: Path = tmp_dir.joinpath(dest_file.name)
            tmp_log: Path = tmp_dir.joinpath("log.txt")
            self.run_process(
                self.dependencies["mdi2tif"][0],
                "-source",
                self.file.get_absolute_path(),
                "-dest",
                tmp_file,
                "-log",
                tmp_log,
            )

            if not self.capture_output and tmp_log.is_file() and (log := tmp_log.read_text().strip()):
                print(log, file=stderr)

            if not tmp_file.is_file():
                raise ConvertError(self.file, "Could not convert file.")

            dest_dir.mkdir(parents=True, exist_ok=True)
            return [tmp_file.replace(dest_file)]
