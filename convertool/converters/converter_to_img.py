from pathlib import Path
from re import match

from .base import Converter


class ConverterToImg(Converter):
    tool_names = ["img"]
    outputs = ["jpg", "png", "tiff"]

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
        dest_dir.mkdir(parents=True, exist_ok=True)

        self.run_process("magick", self.file.get_absolute_path(), dest_file.name, cwd=dest_dir)

        return [dest_file]


class ConverterPDFToImg(ConverterToImg):
    tool_names = ["pdf-to-img"]

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path)
        dest_file: Path = self.output_file(dest_dir, output)
        dest_dir.mkdir(parents=True, exist_ok=True)

        density_stdout, _ = self.run_process("magick", "identify", "-format", r"%x,%y\n", self.file.get_absolute_path())
        density: int = 0

        for density_line in density_stdout.strip().splitlines():
            density_x, _, density_y = density_line.strip().partition(",")
            density_page: int = max(int(density_x), int(density_y), 0) * 2
            if density_page > density:
                density = density_page

        density = density or 150

        self.run_process("magick", "-density", density, self.file.get_absolute_path(), dest_file.name, cwd=dest_dir)

        if output == "tiff":
            return [dest_file]

        return sorted(
            [
                i.relative_to(dest_dir)
                for i in dest_dir.iterdir()
                if i.is_file() and match(rf"^{dest_file.name.split('.')[0]}-\d+.{i.name.split('.', 1)[1]}$", i.name)
            ]
        )


class ConverterTextToImg(ConverterToImg):
    tool_names = ["text-to-img"]

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path)
        dest_file: Path = self.output_file(dest_dir, output)
        text: str = self.file.get_absolute_path().read_text().strip()
        width: int = max(800, max(len(l) * 10 for l in text.splitlines()))
        height: int = max(600, (text.count("\n") + 1) * 25)
        dest_dir.mkdir(parents=True, exist_ok=True)

        self.run_process(
            "magick",
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
