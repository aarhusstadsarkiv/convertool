from pathlib import Path
from typing import ClassVar

from convertool.util import TempDir

from .base import ConverterABC


class ConverterSpreadsheet(ConverterABC):
    tool_names: ClassVar[list[str]] = ["spreadsheet"]
    outputs: ClassVar[list[str]] = ["ods", "pdf", "html"]
    process_timeout: ClassVar[float] = 60.0
    dependencies: ClassVar[dict[str, list[str]]] = {"libreoffice": ["libreoffice", "soffice"]}

    def output_puid(self, output: str) -> str | None:
        if output == "html":
            return "fmt/471"
        return None

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def output_filter(self, output: str) -> str:  # noqa: ARG002
        return ""

    # noinspection DuplicatedCode
    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)
        output_filter: str = self.output_filter(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)

        output_filter = f":{output_filter}" if output_filter else ""

        with TempDir(output_dir) as tmp_dir:
            self.run_process(
                self.dependencies["libreoffice"][0],
                "--headless",
                "--convert-to",
                f"{output}{output_filter}" if output_filter else output,
                "--outdir",
                tmp_dir,
                self.file.get_absolute_path(),
            )
            dest_dir.mkdir(parents=True, exist_ok=True)
            return [f.replace(dest_dir / f.name) for f in tmp_dir.iterdir() if f.is_file()]
