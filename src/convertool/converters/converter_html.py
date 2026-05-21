from pathlib import Path
from subprocess import CalledProcessError
from typing import ClassVar

from convertool.util import TempDir

from .base import _shared_dependencies
from .base import _shared_platforms
from .base import _shared_process_timeout
from .base import ConverterABC
from .base import dummy_base_file
from .converter_pdf import ConverterPDFToImage
from .exceptions import ConvertError


class ConverterHTML(ConverterABC):
    tool_names: ClassVar[list[str]] = ["html", "browser"]
    outputs: ClassVar[list[str]] = ["pdf"]
    dependencies: ClassVar[dict[str, list[str]]] = {"chromium": ["chromium", "chromium-browser", "google-chrome"]}
    process_timeout: ClassVar[float] = 60

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = self.output_file(dest_dir, output)

        with TempDir(output_dir) as tmp_dir:
            tmp_file = tmp_dir.joinpath("output.pdf")
            [_, _, process_result] = self.run_process(
                self.dependencies["chromium"][0],
                "--headless",
                "--no-sandbox",
                f"--print-to-pdf={tmp_file}",
                "--no-pdf-header-footer",
                self.file.get_absolute_path(),
                cwd=tmp_dir,
            )

            if not tmp_file.is_file():
                raise ConvertError(
                    self.file,
                    "Ouptut file not found.",
                    CalledProcessError(
                        process_result.returncode,
                        process_result.args,
                        process_result.stdout,
                        process_result.stderr,
                    ),
                )

            dest_dir.mkdir(parents=True, exist_ok=True)
            tmp_file.replace(dest_file)

        return [dest_file]


class ConverterHTMLToImage(ConverterABC):
    tool_names: ClassVar[list[str]] = ["html", "browser"]
    outputs: ClassVar[list[str]] = ConverterPDFToImage.outputs
    platforms: ClassVar[list[str] | None] = _shared_platforms(ConverterHTML, ConverterPDFToImage)
    dependencies: ClassVar[dict[str, list[str]] | None] = _shared_dependencies(ConverterHTML, ConverterPDFToImage)
    process_timeout: ClassVar[float | None] = _shared_process_timeout(ConverterHTML, ConverterPDFToImage)

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)

        with TempDir(output_dir) as tmp_dir:
            pdfs = ConverterHTML(
                self.file,
                self.root,
                self.relative_root,
                self.database,
                timeout=self.timeout,
                hashed_output_name=self.hashed_output_name,
            ).convert(
                tmp_dir,
                "pdf",
            )
            if not pdfs:
                return []

            pdf = pdfs[0]

            return ConverterPDFToImage(
                dummy_base_file(pdf, tmp_dir),
                tmp_dir,
                tmp_dir,
                self.database,
                timeout=self.timeout,
                hashed_output_name=self.hashed_output_name,
            ).convert(
                output_dir,
                output,
                keep_relative_path=keep_relative_path,
            )
