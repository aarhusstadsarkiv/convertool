from pathlib import Path
from typing import ClassVar

from acacore.models.file import File

from convertool.util import TempDir

from .base import _shared_platforms
from .base import ConverterABC
from .converter_image import ConverterPDFToImage


class ConverterHTML(ConverterABC):
    tool_names: ClassVar[list[str]] = ["html"]
    outputs: ClassVar[list[str]] = ["pdf"]
    dependencies: ClassVar[list[str]] = ["chrome"]
    process_timeout: ClassVar[float] = 60

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = self.output_file(dest_dir, output)

        with TempDir(output_dir) as tmp_dir:
            self.run_process(
                "chrome",
                "--headless",
                "--no-sandbox",
                "--print-to-pdf",
                "--no-pdf-header-footer",
                self.file.get_absolute_path(),
                cwd=tmp_dir,
            )
            dest_dir.mkdir(parents=True, exist_ok=True)
            tmp_dir.joinpath("output.pdf").replace(dest_file)

        return [dest_file]


class ConverterHTMLToImage(ConverterABC):
    tool_names: ClassVar[list[str]] = ["html"]
    outputs: ClassVar[list[str]] = ConverterPDFToImage.outputs
    platforms: ClassVar[list[str] | None] = _shared_platforms(ConverterHTML.platforms, ConverterPDFToImage.platforms)
    dependencies: ClassVar[list[str]] = [  # noqa: SIM222
        *(ConverterHTML.dependencies or []),
        *(ConverterPDFToImage.dependencies or []),
    ] or None
    process_timeout: ClassVar[float | None] = (
        max(
            ConverterHTML.process_timeout or 0,
            ConverterPDFToImage.process_timeout or 0,
        )
        or None
    )

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)

        with TempDir(output_dir) as tmp_dir:
            pdfs = ConverterHTML(self.file, self.database).convert(tmp_dir, "pdf")
            if not pdfs:
                return []

            pdf = pdfs[0]

            return ConverterPDFToImage(File.from_file(pdf, tmp_dir), self.database, tmp_dir).convert(
                output_dir,
                output,
                keep_relative_path=keep_relative_path,
            )
