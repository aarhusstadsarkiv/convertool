from pathlib import Path
from typing import ClassVar

from acacore.models.file import BaseFile

from convertool.util import TempDir

from .base import _shared_platforms
from .base import ConverterABC
from .converter_image import ConverterPDFToImage


class ConverterDocument(ConverterABC):
    tool_names: ClassVar[list[str]] = ["document"]
    outputs: ClassVar[list[str]] = ["odt", "pdf", "html"]
    process_timeout: ClassVar[float] = 60.0
    dependencies: ClassVar[list[str]] = ["libreoffice"]

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def output_filter(self, output: str) -> str:  # noqa: ARG002
        return ""

    # noinspection DuplicatedCode
    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)
        output_filter: str = self.output_filter(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)

        with TempDir(output_dir) as tmp_dir:
            self.run_process(
                "libreoffice",
                "--headless",
                "--convert-to",
                f"{output}:{output_filter}" if output_filter else output,
                "--outdir",
                tmp_dir,
                self.file.get_absolute_path(),
            )
            dest_dir.mkdir(parents=True, exist_ok=True)
            return [f.replace(dest_dir / f.name) for f in tmp_dir.iterdir() if f.is_file()]


class ConverterDocumentToImage(ConverterABC):
    tool_names: ClassVar[list[str]] = ["document"]
    outputs: ClassVar[list[str]] = ConverterPDFToImage.outputs
    platforms: ClassVar[list[str]] = _shared_platforms(ConverterDocument.platforms, ConverterPDFToImage.platforms)
    dependencies: ClassVar[list[str] | None] = [
        *(ConverterDocument.dependencies or []),
        *(ConverterPDFToImage.dependencies or []),
    ] or None
    process_timeout: ClassVar[float | None] = (
        max(
            ConverterDocument.process_timeout or 0,
            ConverterPDFToImage.process_timeout or 0,
        )
        or None
    )

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)

        with TempDir(output_dir) as tmp_dir:
            if not (pdfs := ConverterDocument(self.file, self.database, self.file.root).convert(tmp_dir, "pdf")):
                return []

            pdf = pdfs[0]

            return ConverterPDFToImage(BaseFile.from_file(pdf, tmp_dir), self.database, tmp_dir).convert(
                output_dir,
                output,
                keep_relative_path=keep_relative_path,
            )
