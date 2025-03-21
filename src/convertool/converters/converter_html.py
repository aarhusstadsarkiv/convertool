from pathlib import Path
from typing import ClassVar

from acacore.models.file import BaseFile

from convertool.util import TempDir

from .base import _shared_dependencies
from .base import _shared_platforms
from .base import _shared_process_timeout
from .base import ConverterABC
from .converter_image import ConverterPDFToImage


class ConverterHTML(ConverterABC):
    tool_names: ClassVar[list[str]] = ["html", "browser"]
    outputs: ClassVar[list[str]] = ["pdf"]
    dependencies: ClassVar[list[str]] = ["chromium"]
    process_timeout: ClassVar[float] = 60

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = self.output_file(dest_dir, output)

        with TempDir(output_dir) as tmp_dir:
            tmp_file = tmp_dir.joinpath("output.pdf")
            self.run_process(
                "chromium",
                "--headless",
                "--no-sandbox",
                f"--print-to-pdf={tmp_file}",
                "--no-pdf-header-footer",
                self.file.get_absolute_path(),
                cwd=tmp_dir,
            )
            dest_dir.mkdir(parents=True, exist_ok=True)
            tmp_file.replace(dest_file)

        return [dest_file]


class ConverterHTMLToImage(ConverterABC):
    tool_names: ClassVar[list[str]] = ["html", "browser"]
    outputs: ClassVar[list[str]] = ConverterPDFToImage.outputs
    platforms: ClassVar[list[str] | None] = _shared_platforms(ConverterHTML, ConverterPDFToImage)
    dependencies: ClassVar[list[str]] = _shared_dependencies(ConverterHTML, ConverterPDFToImage)
    process_timeout: ClassVar[float | None] = _shared_process_timeout(ConverterHTML, ConverterPDFToImage)

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)

        with TempDir(output_dir) as tmp_dir:
            pdfs = ConverterHTML(self.file, self.database).convert(tmp_dir, "pdf")
            if not pdfs:
                return []

            pdf = pdfs[0]

            return ConverterPDFToImage(BaseFile.from_file(pdf, tmp_dir), self.database, tmp_dir).convert(
                output_dir,
                output,
                keep_relative_path=keep_relative_path,
            )
