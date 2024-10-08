from pathlib import Path
from typing import ClassVar

from acacore.utils.functions import rm_tree

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

    def output(self, output: str) -> str:
        if output == "jpeg":
            output = "jpg"
        elif output == "tiff":
            output = "tif"
        return super().output(output)

    def convert(
        self,
        output_dir: Path,
        output: str,
        *,
        keep_relative_path: bool = True,
    ) -> list[Path]:
        output = self.output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path)
        dest_file: Path = self.output_file(dest_dir, output)

        self.run_process("convert", self.file.get_absolute_path(), dest_file.name, cwd=dest_dir)

        return [dest_file]


class ConverterPDFToImage(ConverterImage):
    tool_names: ClassVar[list[str]] = ["pdf-to-image"]

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path)
        dest_file: Path = self.output_file(dest_dir, output)
        dest_dir_tmp: Path = dest_dir / f"_{dest_file.name}.imagemagick"
        rm_tree(dest_dir_tmp)

        try:
            dest_dir_tmp.mkdir(parents=True, exist_ok=True)

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
                self.file.get_absolute_path(),
                dest_file.name,
                cwd=dest_dir_tmp,
            )

            return [f.replace(dest_dir / f.name) for f in sorted(dest_dir_tmp.iterdir()) if f.is_file()]
        finally:
            rm_tree(dest_dir_tmp)


class ConverterTextToImage(ConverterImage):
    tool_names: ClassVar[list[str]] = ["text-to-image"]

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path)
        dest_file: Path = self.output_file(dest_dir, output)
        text: str = self.file.get_absolute_path().read_text().strip()
        width: int = max(800, *(len(line) * 10 for line in text.splitlines()), 0)
        height: int = max(600, (text.count("\n") + 1) * 25)

        self.run_process(
            "convert",
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
            dest_file,
        )

        return [dest_file]
