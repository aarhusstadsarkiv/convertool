from pathlib import Path
from typing import ClassVar

from acacore.models.file import BaseFile

from convertool.util import TempDir

from . import resources
from .base import _shared_dependencies
from .base import _shared_platforms
from .base import _shared_process_timeout
from .base import ConverterABC
from .converter_html import ConverterHTML
from .converter_html import ConverterHTMLToImage


class ConverterXSL(ConverterABC):
    tool_names: ClassVar[list[str]] = ["xslt"]
    outputs: ClassVar[list[str]] = ["html", "xml"]
    process_timeout: ClassVar[float] = 10
    dependencies: ClassVar[list[str]] = ["xmlstarlet"]

    def convert(
        self,
        output_dir: Path,
        output: str,
        *,
        keep_relative_path: bool = True,
        xsl: Path | None = None,
    ) -> list[Path]:
        output = self.output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = self.output_file(dest_dir, output)

        with TempDir(output_dir) as tmp_dir:
            tmp_xsl: Path = xsl or tmp_dir.joinpath(f"{tmp_dir.name}.xsl")
            if not xsl:
                tmp_xsl.write_text(
                    '<?xml version="1.0" encoding="UTF-8"?>'
                    '<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"></xsl:stylesheet>',
                    encoding="utf-8",
                )
            stdout, _ = self.run_process(
                "xmlstarlet",
                "tr",
                "" if xsl else "--embed",
                tmp_xsl,
                self.file.get_absolute_path(),
            )

        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_file.write_text(stdout)

        return [dest_file]


class ConverterMedCom(ConverterABC):
    tool_names: ClassVar[list[str]] = ["medcom"]
    outputs: ClassVar[list[str]] = ["html"]
    process_timeout: ClassVar[float] = 10
    dependencies: ClassVar[list[str]] = ["xmlstarlet"]

    def output_puid(self, output: str) -> str | None:
        if output == "html":
            return "fmt/471"
        return None

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = self.output_file(dest_dir, output)

        xsl: Path = resources.medcom.joinpath("viewEmessage.xslt")

        stdout, _ = self.run_process("xmlstarlet", "tr", xsl, self.file.get_absolute_path())

        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_file.write_text(stdout)

        return [dest_file]


class ConverterXSLToPDF(ConverterABC):
    tool_names: ClassVar[list[str]] = ConverterXSL.tool_names
    outputs: ClassVar[list[str]] = ConverterHTML.outputs
    platforms: ClassVar[list[str] | None] = _shared_platforms(ConverterXSL, ConverterHTML)
    dependencies: ClassVar[list[str]] = _shared_dependencies(ConverterXSL, ConverterHTML)
    process_timeout: ClassVar[float | None] = _shared_process_timeout(ConverterXSL, ConverterHTML)

    def convert(
        self,
        output_dir: Path,
        output: str,
        *,
        keep_relative_path: bool = True,
        xsl: Path | None = None,
    ) -> list[Path]:
        output = self.output(output)

        with TempDir(output_dir) as tmp_dir:
            html = ConverterXSL(self.file, self.database).convert(tmp_dir, "html", xsl=xsl)[0]

            return ConverterHTML(BaseFile.from_file(html, tmp_dir), self.database, tmp_dir).convert(
                output_dir,
                output,
                keep_relative_path=keep_relative_path,
            )


class ConverterXSLToImage(ConverterABC):
    tool_names: ClassVar[list[str]] = ConverterXSL.tool_names
    outputs: ClassVar[list[str]] = ConverterHTMLToImage.outputs
    platforms: ClassVar[list[str] | None] = _shared_platforms(ConverterXSL, ConverterHTMLToImage)
    dependencies: ClassVar[list[str]] = _shared_dependencies(ConverterXSL, ConverterHTMLToImage)
    process_timeout: ClassVar[float | None] = _shared_process_timeout(ConverterXSL, ConverterHTMLToImage)

    def convert(
        self,
        output_dir: Path,
        output: str,
        *,
        keep_relative_path: bool = True,
        xsl: Path | None = None,
    ) -> list[Path]:
        output = self.output(output)

        with TempDir(output_dir) as tmp_dir:
            html = ConverterXSL(self.file, self.database).convert(tmp_dir, "html", xsl=xsl)[0]

            return ConverterHTMLToImage(BaseFile.from_file(html, tmp_dir), self.database, tmp_dir).convert(
                output_dir,
                output,
                keep_relative_path=keep_relative_path,
            )


class ConverterMedComToPDF(ConverterABC):
    tool_names: ClassVar[list[str]] = ConverterMedCom.tool_names
    outputs: ClassVar[list[str]] = ConverterHTML.outputs
    platforms: ClassVar[list[str] | None] = _shared_platforms(ConverterMedCom, ConverterHTML)
    dependencies: ClassVar[list[str]] = _shared_dependencies(ConverterMedCom, ConverterHTML)
    process_timeout: ClassVar[float | None] = _shared_process_timeout(ConverterMedCom, ConverterHTML)

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)

        with TempDir(output_dir) as tmp_dir:
            html = ConverterMedCom(self.file, self.database).convert(tmp_dir, "html")[0]

            return ConverterHTML(BaseFile.from_file(html, tmp_dir), self.database, tmp_dir).convert(
                output_dir,
                output,
                keep_relative_path=keep_relative_path,
            )


class ConverterMedComToImage(ConverterABC):
    tool_names: ClassVar[list[str]] = ConverterMedCom.tool_names
    outputs: ClassVar[list[str]] = ConverterHTMLToImage.outputs
    platforms: ClassVar[list[str] | None] = _shared_platforms(ConverterMedCom, ConverterHTMLToImage)
    dependencies: ClassVar[list[str]] = _shared_dependencies(ConverterMedCom, ConverterHTMLToImage)
    process_timeout: ClassVar[float | None] = _shared_process_timeout(ConverterMedCom, ConverterHTMLToImage)

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)

        with TempDir(output_dir) as tmp_dir:
            html = ConverterMedCom(self.file, self.database).convert(tmp_dir, "html")[0]

            return ConverterHTMLToImage(BaseFile.from_file(html, tmp_dir), self.database, tmp_dir).convert(
                output_dir,
                output,
                keep_relative_path=keep_relative_path,
            )
