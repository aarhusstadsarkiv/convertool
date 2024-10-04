from pathlib import Path
from shutil import copy2
from typing import ClassVar

from .base import ConverterABC


class ConverterCopy(ConverterABC):
    tool_names: ClassVar[list[str]] = ["copy"]
    outputs: ClassVar[list[str]] = ["copy"]

    def output_file(self, output_dir: Path, output: str, *, append: bool = False) -> Path:  # noqa: ARG002
        return output_dir / self.file.name

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path)
        dest_file: Path = self.output_file(dest_dir, output)
        copy2(self.file.get_absolute_path(), dest_file)
        return [dest_file]
