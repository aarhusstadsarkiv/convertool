from pathlib import Path
from typing import ClassVar

from acacore.utils.functions import rm_tree

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
        dest_dir_tmp: Path = dest_dir.joinpath(f"_tmp_{self.file.uuid}")
        rm_tree(dest_dir_tmp)
        dest_dir_tmp.mkdir(parents=True, exist_ok=True)

        try:
            self.run_process("ABViewer", "/c", output, f"dir={dest_dir_tmp}", self.file.get_absolute_path())
            return [f.replace(dest_dir / f.name) for f in dest_dir_tmp.iterdir() if f.is_file()]
        finally:
            rm_tree(dest_dir_tmp)
