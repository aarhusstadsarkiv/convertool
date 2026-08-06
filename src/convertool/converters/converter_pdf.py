from pathlib import Path
from typing import ClassVar

from convertool.util import TempDir

from .base import _shared_dependencies
from .base import _shared_platforms
from .base import _shared_process_timeout
from .base import ConverterABC
from .converter_image import ConverterImage
from .exceptions import ConvertError


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


class ConverterPDFToTiff(ConverterABC):
    tool_names: ClassVar[list[str]] = ["pdf"]
    outputs: ClassVar[list[str]] = ["tif", "tiff"]
    dependencies: ClassVar[dict[str, list[str]] | None] = {"pdftoppm": ["pdftoppm"], "tiffcp": ["tiffcp"]}
    platforms: ClassVar[list[str] | None] = None
    process_timeout: ClassVar[float | None] = 300
    multithreading: ClassVar[bool] = False

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]: ...


class ConverterPDFToImage(ConverterImage):
    tool_names: ClassVar[list[str]] = ["pdf"]
    outputs: ClassVar[list[str]] = ConverterImage.outputs
    dependencies: ClassVar[dict[str, list[str]] | None] = _shared_dependencies(ConverterImage, ConverterPDFToTiff)
    platforms: ClassVar[list[str] | None] = _shared_platforms(ConverterImage, ConverterPDFToTiff)
    process_timeout: ClassVar[float | None] = _shared_process_timeout(ConverterImage, ConverterPDFToTiff)
    multithreading: ClassVar[bool] = ConverterImage.multithreading and ConverterPDFToTiff.multithreading

    def convert_tiff(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = self.output_file(dest_dir, output)

        with TempDir(output_dir) as tmp_dir:
            self.run_process(
                self.dependencies["pdftoppm"][0],
                "-tiff",
                "-tiffcompression",
                "lzw",
                "-r",
                150,
                self.file.get_absolute_path(),
                "pg",
                cwd=tmp_dir,
            )

            self.run_process(
                self.dependencies["tiffcp"][0],
                "-c",
                "lzw",
                *sorted(f.name for f in tmp_dir.glob("*.tif")),
                "output.tiff",
                cwd=tmp_dir,
            )

            if not tmp_dir.joinpath("output.tiff").is_file():
                raise ConvertError(self.file, "Output file not found.")

            dest_dir.mkdir(parents=True, exist_ok=True)

            return [tmp_dir.joinpath("output.tiff").replace(dest_file)]

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        if output in ("tiff", "tiff"):
            return self.convert_tiff(output_dir, output, keep_relative_path=keep_relative_path)
        return super().convert(output_dir, output, keep_relative_path=keep_relative_path)
