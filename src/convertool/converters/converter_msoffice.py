from abc import abstractmethod
from pathlib import Path
from typing import ClassVar

from chardet import DetectionDict

from convertool.util import TempDir

from .base import ConverterABC
from .exceptions import ConvertError


class MSOfficeConverter(ConverterABC):
    platforms: ClassVar[list[str]] = ["win32"]
    dependencies: ClassVar[dict[str, list[str]]] = {"docto": ["docto"]}
    _application: ClassVar[str]

    @abstractmethod
    def _file_format(self, output: str) -> tuple[str, list[str]]:
        """
        :param output: The desired output format.
        :return: A tuple containing the export format and any extra arguments required.
        """  # noqa: D205
        ...

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        self.test_output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        file_format, arguments = self._file_format(output)
        dest_file: Path = dest_dir.joinpath(self.output_file(output))

        with TempDir(output_dir) as tmp_dir:
            tmp_file: Path = tmp_dir.joinpath(dest_file.name)
            self.run_process(
                self.dependencies["docto"][0],
                self._application,
                "-f",
                self.file.get_absolute_path(),
                "-T",
                file_format,
                "-O",
                tmp_file,
                *arguments,
            )

            if tmp_file.is_file():
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                return [tmp_file.replace(dest_file)]

            raise ConvertError(self.file, "Could not convert file.")


class MSWordConverter(MSOfficeConverter):
    name: ClassVar[str] = "msword"
    outputs: ClassVar[list[str]] = ["pdf", "pdfa", "odt"]
    _application = "-WD"

    @classmethod
    def output_name(cls, output: str) -> str:
        if output in ("pdf", "pdfa"):
            return "pdf"
        if output == "odt":
            return "document"
        return output

    def output_extension(self, output: str) -> str:
        if output in ("pdf", "pdfa"):
            return ".pdf"
        if output == "odt":
            return ".odt"
        return super().output_extension(output)

    def _file_format(self, output: str) -> tuple[str, list[str]]:
        if output == "pdf":
            return "wdFormatPDF", []
        if output == "pdfa":
            return "wdFormatPDF", ["--use-ISO190051"]
        if output == "odt":
            return "wdFormatOpenDocumentText", []

        raise KeyError(f"Unknown output {output}")


class MSExcelConverter(MSOfficeConverter):
    name: ClassVar[str] = "msexcel"
    outputs: ClassVar[list[str]] = ["pdf", "ods", "html"]
    _application = "-XL"

    @classmethod
    def output_name(cls, output: str) -> str:
        if output == "pdf":
            return "pdf"
        if output == "ods":
            return "spreadsheet"
        if output == "html":
            return "html"
        return output

    def output_extension(self, output: str) -> str:
        if output == "pdf":
            return ".pdf"
        if output == "ods":
            return ".ods"
        if output == "html":
            return ".html"
        return super().output_extension(output)

    def output_puid(self, output: str) -> str | None:
        if output == "html":
            return "fmt/471"
        return None

    def output_encoding(self, output: str) -> DetectionDict | None:
        if output == "html":
            return DetectionDict(encoding="utf-8", confidence=1.0, language=None, mime_type="text/html")
        return None

    def _file_format(self, output: str) -> tuple[str, list[str]]:
        if output == "pdf":
            return "xlPDF", []
        if output == "ods":
            return "xlOpenDocumentSpreadsheet", []
        if output == "html":
            return "xlHtml", []

        raise KeyError(f"Unknown output {output}")


class MSPowerPointConverter(MSOfficeConverter):
    name: ClassVar[str] = "mspowerpoint"
    outputs: ClassVar[list[str]] = ["pdf", "odp"]
    _application = "-PP"

    @classmethod
    def output_name(cls, output: str) -> str:
        if output == "pdf":
            return "pdf"
        if output == "odp":
            return "presentation"
        return output

    def output_extension(self, output: str) -> str:
        if output == "pdf":
            return ".pdf"
        if output == "odp":
            return ".odp"
        return super().output_extension(output)

    def _file_format(self, output: str) -> tuple[str, list[str]]:
        if output == "pdf":
            return "ppSaveAsPDF", []
        if output == "odp":
            return "ppSaveAsOpenDocumentPresentation", []

        raise KeyError(f"Unknown output {output}")
