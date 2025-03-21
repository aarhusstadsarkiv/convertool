from pathlib import Path
from typing import ClassVar

from convertool.util import TempDir

from .base import ConverterABC


class ConverterXSL(ConverterABC):
    tool_names: ClassVar[list[str]] = ["xsl"]
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

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = self.output_file(dest_dir, output)

        xsl: Path = Path(__file__).parent.joinpath("resources", "medcom", "viewEmessage.xslt")

        stdout, _ = self.run_process("xmlstarlet", "tr", xsl, self.file.get_absolute_path())

        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_file.write_text(stdout)

        return [dest_file]
