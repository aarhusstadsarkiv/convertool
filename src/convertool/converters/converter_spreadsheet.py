from pathlib import Path
from typing import ClassVar

from chardet import DetectionDict

from convertool.util import TempDir

from .base import ConverterABC
from .base import hashed_file_name


class SpreadsheetConverter(ConverterABC):
    name: ClassVar[str] = "spreadsheet"
    outputs: ClassVar[list[str]] = ["ods", "pdf", "html"]
    process_timeout: ClassVar[float] = 60.0
    dependencies: ClassVar[dict[str, list[str]]] = {"libreoffice": ["libreoffice", "soffice"]}

    @classmethod
    def output_name(cls, output: str) -> str:
        if output == "ods":
            return "spreadsheet"
        if output == "pdf":
            return "pdf"
        if output == "html":
            return "html"
        return output

    def output_extension(self, output: str) -> str:
        if output == "ods":
            return ".ods"
        if output == "pdf":
            return ".pdf"
        if output == "html":
            return ".html"
        return f".{output}"

    def output_puid(self, output: str) -> str | None:
        if output == "html":
            return "fmt/471"
        return None

    def output_encoding(self, output: str) -> DetectionDict | None:
        if output == "html":
            return DetectionDict(encoding="utf-8", confidence=1.0, language=None, mime_type="text/html")
        return None

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def output_filter(self, output: str) -> str:
        if output == "pdf":
            return 'impress_pdf_Export:{"SelectPdfVersion":3}'
        return ""

    # noinspection DuplicatedCode
    def converter(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        self.test_output(output)
        output_filter: str = self.output_filter(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)

        output_files: list[Path] = []

        with TempDir(output_dir) as tmp_dir:
            self.run_process(
                self.dependencies["libreoffice"][0],
                "--headless",
                "--convert-to",
                f"{output}:{output_filter}" if output_filter else output,
                "--outdir",
                f"-env:UserInstallation={tmp_dir.joinpath('_libreoffice').as_uri()}",
                tmp_dir,
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
