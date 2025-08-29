from pathlib import Path
from typing import ClassVar

from convertool.util import TempDir

from .base import ConverterABC
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

            if tmp_file.is_file():
                dest_dir.mkdir(parents=True, exist_ok=True)
                return [tmp_file.replace(dest_file)]

        raise ConvertError(self.file, "Could not convert file.")
