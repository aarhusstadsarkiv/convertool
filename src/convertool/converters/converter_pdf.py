from pathlib import Path
from typing import ClassVar

from convertool.util import TempDir

from .base import ConverterABC
from .converter_image import ImageConverter
from .exceptions import BadOption


class PDFConverter(ConverterABC):
    name: ClassVar[str] = "pdf"
    outputs: ClassVar[list[str]] = ["pdfa-1", "pdfa-2", "pdfa-3"]
    dependencies: ClassVar[dict[str, list[str]]] = {"ghostscript": ["gs"]}

    @classmethod
    def output_name(cls, output: str) -> str:
        return "pdf"

    def output_extension(self, output: str) -> str:
        return ".pdf"

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        self.test_output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = dest_dir.joinpath(self.output_file(output))
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

            return [tmp_dir.joinpath(dest_file.name).replace(dest_file)]


class PDFToImageConverter(ConverterABC):
    name: ClassVar[str] = PDFConverter.name
    outputs: ClassVar[list[str]] = ["tiff", "jpeg", "png"]
    dependencies: ClassVar[dict[str, list[str]]] = {"pdftoppm": ["pdftoppm"], "tiffcp": ["tiffcp"]}
    platforms: ClassVar[list[str] | None] = None
    process_timeout: ClassVar[int] = 300
    multithreading: ClassVar[bool] = False

    @classmethod
    def output_name(cls, output: str) -> str:
        return "image"

    def output_extension(self, output: str) -> str:
        return ".tif"

    def output_puid(self, output: str) -> str | None:
        if output == "jpeg":
            return "fmt/44"
        if output == "tiff":
            return "fmt/353"
        if output in ("png",):
            return "fmt/12"
        return None

    def test_options(self):
        if (dpi := self.options.get("dpi")) is not None:
            if isinstance(dpi, str) and not dpi.isdigit():
                raise BadOption(f"Invalid value {dpi!r} for 'dpi' option.")
            if isinstance(dpi, int) and dpi <= 0:
                raise BadOption(f"Invalid value {dpi} for 'dpi' option.")

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        self.test_output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = dest_dir.joinpath(self.output_file(output))
        args: list[str] = []
        outputs: list[Path]

        if output == "tiff":
            args = ["-tiff", "-tiffcompression", "lzw"]
        elif output == "jpeg":
            args = ["-jpeg"]
        elif output in ("png",):
            args = ["-png"]

        with TempDir(output_dir) as tmp_dir:
            self.run_process(
                self.dependencies["pdftoppm"][0],
                *args,
                "-r",
                self.options.get("dpi", 150),
                self.file.get_absolute_path(),
                dest_file.stem,
                cwd=tmp_dir,
            )

            if output == "tiff":
                self.run_process(
                    self.dependencies["tiffcp"][0],
                    "-c",
                    "lzw",
                    *sorted(f.name for f in tmp_dir.glob("*.tif")),
                    dest_file.name,
                    cwd=tmp_dir,
                )

                outputs = [tmp_dir.joinpath(dest_file.name)]
            else:
                outputs = sorted(tmp_dir.iterdir())

            dest_dir.mkdir(parents=True, exist_ok=True)

            return [o.replace(dest_dir.joinpath(o.name)) for o in outputs]


class PDFToImageFallbackConverter(ImageConverter):
    name: ClassVar[str] = PDFConverter.name
    outputs: ClassVar[list[str]] = [o for o in ImageConverter.outputs if o not in PDFToImageConverter.outputs]
    dependencies: ClassVar[dict[str, list[str]] | None] = ImageConverter.dependencies
    platforms: ClassVar[list[str] | None] = ImageConverter.platforms
    process_timeout: ClassVar[int | None] = ImageConverter.process_timeout
    multithreading: ClassVar[bool] = ImageConverter.multithreading
