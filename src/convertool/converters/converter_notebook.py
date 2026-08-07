from os import chdir
from pathlib import Path
from typing import ClassVar

import nbformat
from chardet import DetectionDict
from nbconvert import HTMLExporter

from convertool.util import TempDir

from .base import ConverterABC


class IPYNBConverter(ConverterABC):
    name: ClassVar[str] = "ipynb"
    outputs: ClassVar[list[str]] = ["html"]

    def output_puid(self, output: str) -> str | None:
        if output == "html":
            return "fmt/471"
        return None

    def output_encoding(self, output: str) -> DetectionDict | None:
        if output == "html":
            return DetectionDict(encoding="utf-8", confidence=1.0, language=None, mime_type="text/html")
        return None

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        self.test_output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = dest_dir.joinpath(self.output_file(output))

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
