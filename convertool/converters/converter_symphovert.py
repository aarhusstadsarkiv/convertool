from pathlib import Path
from typing import ClassVar

from .base import ConverterABC
from .exceptions import ConvertError


class ConverterSymphovert(ConverterABC):
    tool_names: ClassVar[list[str]] = ["symphovert"]
    outputs: ClassVar[list[str]] = ["odt", "ods", "odp"]

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path)
        dest_file: Path = self.output_file(dest_dir, output)

        if dest_file.is_file():
            return [dest_file]

        raise ConvertError(self.file, f"Converted file {str(dest_file.relative_to(output_dir))!r} not found")
