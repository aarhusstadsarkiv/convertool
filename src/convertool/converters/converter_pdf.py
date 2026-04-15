from pathlib import Path
from typing import ClassVar

import pdf2image
from pdf2image.exceptions import PDFInfoNotInstalledError
from pdf2image.exceptions import PDFPageCountError
from pdf2image.exceptions import PDFSyntaxError

from convertool.util import TempDir

from .base import ConverterABC
from .converter_image import ConverterImage
from .exceptions import ConvertError
from .exceptions import OutputTargetError


class ConverterPDF(ConverterABC):
    tool_names: ClassVar[list[str]] = ["pdf"]
    outputs: ClassVar[list[str]] = ["pdfa-1", "pdfa-2", "pdfa-3"]
    dependencies: ClassVar[dict[str, list[str]]] = {"ghostscript": ["gs"]}

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = self.output_file(dest_dir, "pdf")
        arguments: list[str] = []

        if output == "pdf-a1":
            arguments.extend(["-dPDFA=1", "-dPDFACompatibilityPolicy=1"])
        elif output == "pdf-a2":
            arguments.extend(["-dPDFA=2", "-dPDFACompatibilityPolicy=1"])
        elif output == "pdf-a3":
            arguments.extend(["-dPDFA=3", "-dPDFACompatibilityPolicy=1"])

        with TempDir(output_dir) as tmp_dir:
            self.run_process(
                self.dependencies["ghostscript"][0],
                "-dNOSAFER",
                "-dNOPAUSE",
                "-dBATCH",
                "-sDEVICE=pdfwrite",
                "-sColorConversionStrategy=UseDeviceIndependentColor",
                f"-sOutputFile={dest_file.name}",
                *arguments,
                self.file.get_absolute_path(),
                cwd=tmp_dir,
            )
            dest_dir.mkdir(parents=True, exist_ok=True)
            tmp_dir.joinpath(dest_file.name).replace(dest_file)

        return [dest_file]


class ConverterPDFToImage(ConverterABC):
    tool_names: ClassVar[list[str]] = ["pdf"]
    outputs: ClassVar[list[str]] = [
        "jpg",
        "jpeg",
        "png",
        "tif",
        "tiff",
    ]
    dependencies: ClassVar[dict[str, list[str]]] = {"pdftoppm": ["pdftoppm"], "pdftocairo": ["pdftocairo"]}

    def output(self, output: str) -> str:
        if output == "jpeg":
            output = "jpg"
        elif output == "tiff":
            output = "tif"
        return super().output(output)

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = self.output_file(dest_dir, output)

        with TempDir(output_dir) as tmp_dir:
            try:
                pdf2image.convert_from_path(
                    self.file.get_absolute_path(),
                    fmt=output,
                    output_folder=str(tmp_dir),
                    output_file=str(tmp_dir.joinpath(dest_file.stem)),
                    single_file=output in ("tiff", "tif"),
                    paths_only=True,
                )
            except (PDFInfoNotInstalledError, PDFPageCountError, PDFSyntaxError) as err:
                raise ConvertError(self.file, err)

            dest_dir.mkdir(parents=True, exist_ok=True)

            return [f.replace(dest_dir.joinpath(f.name)) for f in sorted(tmp_dir.iterdir()) if f.is_file()]


class ConverterPDFToJPEG2000(ConverterImage):
    tool_names: ClassVar[list[str]] = ["pdf"]
    outputs: ClassVar[list[str]] = ["jp2"]

    def output(self, output: str) -> str:
        if output in ("jp2",):
            return "jp2"
        raise OutputTargetError(self.file, f"Unsupported output {output}")

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = self.output_file(dest_dir, output)
        args: list[str] = []

        density, _ = self.image_dpi(self.file.get_absolute_path())
        density *= 2

        with TempDir(output_dir) as tmp_dir:
            self.run_process(
                self.dependencies["imagemagick"][0],
                "-density",
                density,
                "-background",
                "white",
                *args,
                self.file.get_absolute_path(),
                dest_file.name,
                cwd=tmp_dir,
            )

            dest_dir.mkdir(parents=True, exist_ok=True)

            return [f.replace(dest_dir / f.name) for f in sorted(tmp_dir.iterdir()) if f.is_file()]
