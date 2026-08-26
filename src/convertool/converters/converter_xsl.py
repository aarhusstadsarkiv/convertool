from pathlib import Path
from typing import ClassVar

from chardet import DetectionDict

from convertool.util import TempDir

from . import resources
from .base import ConverterABC


class XSLConverter(ConverterABC):
    name: ClassVar[str] = "xslt"
    outputs: ClassVar[list[str]] = ["html", "xml"]
    process_timeout: ClassVar[float] = 10
    use_process: ClassVar[bool] = True
    dependencies: ClassVar[dict[str, list[str]]] = {"xmlstarlet": ["xmlstarlet"]}

    @classmethod
    def output_name(cls, output: str) -> str:
        if output == "html":
            return "html"
        if output == "xml":
            return "xml"
        return output

    def output_extension(self, output: str) -> str:
        if output == "html":
            return ".html"
        if output == "xml":
            return ".xml"
        return f".{output}"

    def output_puid(self, output: str) -> str | None:
        if output == "html":
            return "fmt/471"
        if output == "xml":
            return "fmt/101"
        return None

    def output_encoding(self, output: str) -> DetectionDict | None:
        if output == "html":
            return DetectionDict(encoding="utf-8", confidence=1.0, language=None, mime_type="text/html")
        if output == "xml":
            return DetectionDict(encoding="utf-8", confidence=1.0, language=None, mime_type="application/xml")
        return None

    def converter(
        self,
        output_dir: Path,
        output: str,
        *,
        keep_relative_path: bool = True,
        xsl: Path | None = None,
    ) -> list[Path]:
        self.test_output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = dest_dir.joinpath(self.output_filename(output))

        with TempDir(output_dir) as tmp_dir:
            tmp_xsl: Path = xsl or tmp_dir.joinpath(f"{tmp_dir.name}.xsl")
            if not xsl:
                tmp_xsl.write_text(
                    '<?xml version="1.0" encoding="UTF-8"?>'
                    '<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"></xsl:stylesheet>',
                    encoding="utf-8",
                )
            stdout, _, _ = self.run_process(
                self.dependencies["xmlstarlet"][0],
                "tr",
                "" if xsl else "--embed",
                tmp_xsl,
                self.file.get_absolute_path(),
            )

        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_file.write_text(stdout, encoding="utf-8")

        return [dest_file]


class MedComConverter(ConverterABC):
    name: ClassVar[str] = "medcom"
    outputs: ClassVar[list[str]] = ["html"]
    process_timeout: ClassVar[float] = 10
    dependencies: ClassVar[dict[str, list[str]]] = {"xmlstarlet": ["xmlstarlet"]}

    @classmethod
    def output_name(cls, output: str) -> str:
        return "html"

    def output_extension(self, output: str) -> str:
        return ".html"

    def output_puid(self, output: str) -> str | None:
        return "fmt/471"

    def output_encoding(self, output: str) -> DetectionDict | None:
        return DetectionDict(encoding="utf-8", confidence=1.0, language=None, mime_type="text/html")

    def converter(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        self.test_output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = dest_dir.joinpath(self.output_filename(output))

        xsl: Path = resources.medcom.joinpath("viewEmessage.xslt")

        stdout, _, _ = self.run_process(self.dependencies["xmlstarlet"][0], "tr", xsl, self.file.get_absolute_path())

        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_file.write_text(stdout, encoding="utf-8")

        return [dest_file]
