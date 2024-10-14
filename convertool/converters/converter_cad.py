from pathlib import Path
from typing import ClassVar

from .base import ConverterABC


class ConverterCAD(ConverterABC):
    tool_names: ClassVar[list[str]] = ["cad"]
    outputs: ClassVar[list[str]] = ["dxf", "pdf", "svg"]
    process_timeout: ClassVar[float] = 120
    platforms: ClassVar[list[str]] = ["win32"]
    dependencies: ClassVar[list[str]] = ["ABViewer"]

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path)
        dest_file: Path = self.output_file(dest_dir, output)

        self.run_process("ABViewer", "/c", output, f"dir={output_dir}", self.file.get_absolute_path())

        return [dest_file]
