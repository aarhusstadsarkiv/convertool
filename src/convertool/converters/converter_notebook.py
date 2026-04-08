from os import chdir
from pathlib import Path
from typing import ClassVar

import nbformat
from nbconvert import HTMLExporter

from convertool.util import TempDir

from .base import _shared_dependencies
from .base import _shared_platforms
from .base import _shared_process_timeout
from .base import ConverterABC
from .base import dummy_base_file
from .converter_html import ConverterHTML
from .converter_html import ConverterHTMLToImage


class ConverterIPYNBToHTML(ConverterABC):
    tool_names: ClassVar[list[str]] = ["ipynb"]
    outputs: ClassVar[list[str]] = ["html"]

    def output_puid(self, output: str) -> str | None:
        if output == "html":
            return "fmt/471"
        return None

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = self.output_file(dest_dir, output)

        with self.file.get_absolute_path().open(encoding=(self.file.encoding or {}).get("encoding")) as f:
            notebook = nbformat.reads(f.read(), as_version=nbformat.NO_CONVERT)

        cwd = Path.cwd()

        try:
            chdir(self.file.get_absolute_path().parent)
            body, _ = HTMLExporter(template_name="classic", embed_images=True).from_notebook_node(notebook)
        finally:
            chdir(cwd)

        with TempDir(output_dir) as tmp_dir:
            tmp_file = tmp_dir.joinpath(dest_file.name)
            tmp_file.write_text(body, encoding="utf-8")
            dest_dir.mkdir(parents=True, exist_ok=True)
            return [tmp_file.replace(dest_file)]


class ConverterIPYNBToPDF(ConverterABC):
    tool_names: ClassVar[list[str]] = ["ipynb"]
    outputs: ClassVar[list[str]] = ["pdf"]
    platforms: ClassVar[list[str] | None] = _shared_platforms(ConverterIPYNBToHTML, ConverterHTML)
    dependencies: ClassVar[dict[str, list[str]] | None] = _shared_dependencies(ConverterIPYNBToHTML, ConverterHTML)
    process_timeout: ClassVar[float | None] = _shared_process_timeout(ConverterIPYNBToHTML, ConverterHTML)

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)

        with TempDir(output_dir) as tmp_dir:
            htmls = ConverterIPYNBToHTML(self.file, self.database, hashed_output_name=self.hashed_output_name).convert(
                tmp_dir, "html"
            )
            if not htmls:
                return []

            html = htmls[0]

            return ConverterHTML(
                dummy_base_file(html, tmp_dir),
                self.database,
                tmp_dir,
                hashed_output_name=self.hashed_output_name,
            ).convert(
                output_dir,
                output,
                keep_relative_path=keep_relative_path,
            )


class ConverterIPYNBToImage(ConverterABC):
    tool_names: ClassVar[list[str]] = ["ipynb"]
    outputs: ClassVar[list[str]] = ConverterHTMLToImage.outputs
    platforms: ClassVar[list[str] | None] = _shared_platforms(ConverterIPYNBToHTML, ConverterHTMLToImage)
    dependencies: ClassVar[dict[str, list[str]] | None] = _shared_dependencies(
        ConverterIPYNBToHTML,
        ConverterHTMLToImage,
    )
    process_timeout: ClassVar[float | None] = _shared_process_timeout(ConverterIPYNBToHTML, ConverterHTMLToImage)

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)

        with TempDir(output_dir) as tmp_dir:
            htmls = ConverterIPYNBToHTML(self.file, self.database, hashed_output_name=self.hashed_output_name).convert(
                tmp_dir, "html"
            )
            if not htmls:
                return []

            html = htmls[0]

            return ConverterHTMLToImage(
                dummy_base_file(html, tmp_dir),
                self.database,
                tmp_dir,
                hashed_output_name=self.hashed_output_name,
            ).convert(
                output_dir,
                output,
                keep_relative_path=keep_relative_path,
            )
