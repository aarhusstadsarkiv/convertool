from pathlib import Path
from tempfile import TemporaryDirectory
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
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)

        with TemporaryDirectory() as tmp_dir:
            tmp_dir = Path(tmp_dir)
            self.run_process("ABViewer", "/c", output, f"dir={tmp_dir}", self.file.get_absolute_path())
            dest_dir.mkdir(parents=True, exist_ok=True)
            return [f.replace(dest_dir / f.name) for f in tmp_dir.iterdir() if f.is_file()]
