from pathlib import Path
from typing import ClassVar

from .base import Converter


class ConverterMsg(Converter):
    tool_names: ClassVar[list[str]] = ["msg"]
    outputs: ClassVar[list[str]] = ["txt", "html"]

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        return []
