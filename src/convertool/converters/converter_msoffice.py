from abc import abstractmethod
from pathlib import Path
from typing import ClassVar

from convertool.converters import ConverterABC
from convertool.converters.exceptions import ConvertError
from convertool.util import TempDir


class ConverterMSOffice(ConverterABC):
    platforms: ClassVar[list[str]] = ["win32"]
    dependencies: ClassVar[list[str]] = ["docto"]
    _application: ClassVar[str]

    @abstractmethod
    def _file_format(self, output: str) -> tuple[str, str, list[str]]:
        """
        :param output: The desired output format.
        :return: A tuple containing the export format, the extension, and any extra arguments required.
        """  # noqa: D205
        ...

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        file_format, extension, arguments = self._file_format(output)
        dest_file: Path = self.output_file(dest_dir, extension)

        with TempDir(output_dir) as tmp_dir:
            tmp_file: Path = tmp_dir.joinpath(dest_file.name)
            self.run_process(
                "docto",
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
                return [tmp_file.replace(dest_file)]

            raise ConvertError(self.file, "Could not convert file.")


class ConverterMSWord(ConverterMSOffice):
    tool_names: ClassVar[list[str]] = ["msword"]
    outputs: ClassVar[list[str]] = ["pdf", "pdfa", "odt"]
    _application = "-WD"

    def _file_format(self, output: str) -> tuple[str, str, list[str]]:
        if output == "pdf":
            return "wdFormatPDF", "pdf", []
        if output == "pdfa":
            return "wdFormatPDF", "pdf", ["--use-ISO190051"]
        if output == "odt":
            return "wdFormatOpenDocumentText", "odt", []

        raise KeyError(f"Unknown output {output}")


class ConverterMSExcel(ConverterMSOffice):
    tool_names: ClassVar[list[str]] = ["msexcel"]
    outputs: ClassVar[list[str]] = ["pdf", "ods", "html"]
    _application = "-XL"

    def _file_format(self, output: str) -> tuple[str, str, list[str]]:
        if output == "pdf":
            return "xlPDF", "pdf", []
        if output == "ods":
            return "xlOpenDocumentSpreadsheet", "ods", []
        if output == "html":
            return "xlHtml", "html", []

        raise KeyError(f"Unknown output {output}")


class ConverterMSPowerPoint(ConverterMSOffice):
    tool_names: ClassVar[list[str]] = ["mspowerpoint"]
    outputs: ClassVar[list[str]] = ["pdf", "odp"]
    _application = "-PP"

    def _file_format(self, output: str) -> tuple[str, str, list[str]]:
        if output == "pdf":
            return "ppSaveAsPDF", "pdf", []
        if output == "odp":
            return "ppSaveAsOpenDocumentPresentation", "odp", []

        raise KeyError(f"Unknown output {output}")
