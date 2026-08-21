from pathlib import Path
from typing import ClassVar

from convertool.util import TempDir

from .base import ConverterABC
from .base import hashed_file_name


class CADConverter(ConverterABC):
    name: ClassVar[str] = "cad"
    outputs: ClassVar[list[str]] = ["dxf", "pdf", "svg"]
    process_timeout: ClassVar[float] = 120
    use_process: ClassVar[bool] = True
    platforms: ClassVar[list[str]] = ["win32"]
    dependencies: ClassVar[dict[str, list[str]]] = {"abviewer": ["ABViewer"]}

    @classmethod
    def output_name(cls, output: str) -> str:
        if output == "dxf":
            return "cad"
        if output == "pdf":
            return "pdf"
        if output == "svg":
            return "vector"
        return output

    def output_extension(self, output: str) -> str:
        if output == "dxf":
            return ".dxf"
        if output == "pdf":
            return ".pdf"
        if output == "svg":
            return ".svg"
        return f".{output}"

    def output_puid(self, output: str) -> str | None:
        if output == "svg":
            return "fmt/413"
        return None

    def converter(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        self.test_output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        output_files: list[Path] = []

        with TempDir(output_dir) as tmp_dir:
            self.run_process(
                self.dependencies["abviewer"][0],
                "/c",
                output,
                f"dir={tmp_dir}",
                self.file.get_absolute_path(),
            )
            dest_dir.mkdir(parents=True, exist_ok=True)

            for f in tmp_dir.iterdir():
                if not f.is_file():
                    continue
                if self.hashed_output_name:
                    output_files.append(f.replace(dest_dir / hashed_file_name(self.file.relative_path / f.name)))
                else:
                    output_files.append(f.replace(dest_dir / f.name))

        return output_files
