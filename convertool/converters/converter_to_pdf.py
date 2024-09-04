from pathlib import Path
from typing import ClassVar

from .base import Converter


class ConverterToPdf(Converter):
    tool_names: ClassVar[list[str]] = ["pdf"]
    outputs: ClassVar[list[str]] = [
        "pdf-a1",
        "pdf-a2",
        "pdf-a3",
    ]

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path)
        dest_file: Path = self.output_file(dest_dir, "pdf")
        arguments: list[str] = []

        if output == "pdf-a1":
            arguments.extend(["-dPDFA=1", "-dPDFACompatibilityPolicy=1"])
        elif output == "pdf-a2":
            arguments.extend(["-dPDFA=2", "-dPDFACompatibilityPolicy=1"])
        elif output == "pdf-a3":
            arguments.extend(["-dPDFA=3", "-dPDFACompatibilityPolicy=1"])

        self.run_process(
            "gs",
            "-dNOSAFER",
            "-dNOPAUSE",
            "-dBATCH",
            "-sDEVICE=pdfwrite",
            "-sColorConversionStrategy=UseDeviceIndependentColor",
            f"-sOutputFile={dest_file.name}",
            *arguments,
            self.file.get_absolute_path(),
            cwd=dest_dir,
        )

        return [dest_file]
