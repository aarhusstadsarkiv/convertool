from pathlib import Path
from tempfile import TemporaryDirectory
from typing import ClassVar

from .base import ConverterABC


class ConverterImage(ConverterABC):
    tool_names: ClassVar[list[str]] = ["image"]
    outputs: ClassVar[list[str]] = [
        "jpg",
        "jpeg",
        "png",
        "tif",
        "tiff",
        "jp2",
    ]
    process_timeout: ClassVar[float] = 180.0
    dependencies: ClassVar[list[str]] = ["convert"]

    def output(self, output: str) -> str:
        if output == "jpeg":
            output = "jpg"
        elif output == "tiff":
            output = "tif"
        return super().output(output)

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path, mkdir=False)
        dest_file: Path = self.output_file(dest_dir, output)

        with TemporaryDirectory() as tmp_dir:
            tmp_dir = Path(tmp_dir)
            self.run_process("convert", self.file.get_absolute_path(), dest_file.name, cwd=tmp_dir)
            dest_dir.mkdir(parents=True, exist_ok=True)
            tmp_dir.joinpath(dest_file.name).replace(dest_file)

        return [dest_file]


class ConverterPDFToImage(ConverterImage):
    tool_names: ClassVar[list[str]] = ["pdf-to-image"]

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path, mkdir=False)
        dest_file: Path = self.output_file(dest_dir, output)

        with TemporaryDirectory() as tmp_dir:
            tmp_dir = Path(tmp_dir)
            density_stdout, _ = self.run_process("identify", "-format", r"%x,%y\n", self.file.get_absolute_path())
            density: int = 0

            for density_line in density_stdout.strip().splitlines():
                density_x, _, density_y = density_line.strip().partition(",")
                density_page: int = max(int(density_x), int(density_y), 0) * 2
                if density_page > density:
                    density = density_page

            density = density or 150

            self.run_process(
                "convert",
                "-density",
                density,
                "-compress",
                "LZW",
                self.file.get_absolute_path(),
                dest_file.name,
                cwd=tmp_dir,
            )

            dest_dir.mkdir(parents=True, exist_ok=True)

            return [f.replace(dest_dir / f.name) for f in sorted(tmp_dir.iterdir()) if f.is_file()]


class ConverterTextToImage(ConverterImage):
    tool_names: ClassVar[list[str]] = ["text-to-image"]

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path, mkdir=False)
        dest_file: Path = self.output_file(dest_dir, output)
        text: str = self.file.get_absolute_path().read_text().strip()
        width: int = max(800, *(len(line) * 10 for line in text.splitlines()), 0)
        height: int = max(600, (text.count("\n") + 1) * 25)

        with TemporaryDirectory() as tmp_dir:
            tmp_dir = Path(tmp_dir)
            self.run_process(
                "convert",
                "-compress",
                "LZW",
                "-size",
                f"{width}x{height}",
                "xc:white",
                "-fill",
                "black",
                "-pointsize",
                "20",
                "-annotate",
                "+5+20",
                text,
                dest_file.name,
                cwd=tmp_dir,
            )
            dest_dir.mkdir(parents=True, exist_ok=True)
            tmp_dir.joinpath(dest_file.name).replace(dest_file)

        return [dest_file]
