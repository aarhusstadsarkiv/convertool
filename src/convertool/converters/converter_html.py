from pathlib import Path
from typing import ClassVar

from weasyprint import HTML

from convertool.util import TempDir

from .base import ConverterABC


class HTMLConverter(ConverterABC):
    name: ClassVar[str] = "html"
    outputs: ClassVar[list[str]] = ["pdf"]

    @classmethod
    def output_name(cls, output: str) -> str:  # noqa: ARG003
        return "pdf"

    def output_extension(self, output: str) -> str:  # noqa: ARG002
        return ".pdf"

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        self.test_output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = dest_dir.joinpath(self.output_file(output))

        with TempDir(output_dir) as tmp_dir:
            HTML(filename=self.file.get_absolute_path()).write_pdf(tmp_file := tmp_dir.joinpath(dest_file.name))

            dest_dir.mkdir(parents=True, exist_ok=True)

            tmp_file.replace(dest_file)

        return [dest_file]
