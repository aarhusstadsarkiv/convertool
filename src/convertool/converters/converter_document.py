from pathlib import Path
from typing import ClassVar

from convertool.util import TempDir

from .base import _shared_dependencies
from .base import _shared_platforms
from .base import _shared_process_timeout
from .base import ConverterABC
from .base import dummy_base_file
from .converter_image import ConverterPDFToImage


class ConverterDocument(ConverterABC):
    tool_names: ClassVar[list[str]] = ["document"]
    outputs: ClassVar[list[str]] = ["odt", "pdf", "html"]
    process_timeout: ClassVar[float] = 60.0
    dependencies: ClassVar[dict[str, list[str]]] = {"libreoffice": ["libreoffice", "soffice"]}

    def output_puid(self, output: str) -> str | None:
        if output == "html":
            return "fmt/471"
        return None

    # noinspection PyMethodMayBeStatic
    def output_filter(self, output: str) -> str:
        if output == "pdf":
            return 'writer_pdf_Export:{"SelectPdfVersion":3}'
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
                f"-env:UserInstallation={tmp_dir.joinpath('_libreoffice').as_uri()}",
                self.file.get_absolute_path(),
            )
            dest_dir.mkdir(parents=True, exist_ok=True)
            return [f.replace(dest_dir / f.name) for f in tmp_dir.iterdir() if f.is_file()]


class ConverterDocumentToImage(ConverterABC):
    tool_names: ClassVar[list[str]] = ["document"]
    outputs: ClassVar[list[str]] = ConverterPDFToImage.outputs
    platforms: ClassVar[list[str]] = _shared_platforms(ConverterDocument, ConverterPDFToImage)
    dependencies: ClassVar[list[str] | None] = _shared_dependencies(ConverterDocument, ConverterPDFToImage)
    process_timeout: ClassVar[float | None] = _shared_process_timeout(ConverterDocument, ConverterPDFToImage)

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)

        with TempDir(output_dir) as tmp_dir:
            if not (pdfs := ConverterDocument(self.file, self.database, self.file.root).convert(tmp_dir, "pdf")):
                return []

            pdf = pdfs[0]

            return ConverterPDFToImage(dummy_base_file(pdf, tmp_dir), self.database, tmp_dir).convert(
                output_dir,
                output,
                keep_relative_path=keep_relative_path,
            )
