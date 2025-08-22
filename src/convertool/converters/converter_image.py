from pathlib import Path
from typing import ClassVar

from convertool.util import TempDir

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
        "pdf",
    ]
    process_timeout: ClassVar[float] = 180.0
    dependencies: ClassVar[dict[str, list[str]]] = {"imagemagick": ["magick", "convert"]}

    def image_dpi(self, file: Path, default_density: int = 150) -> tuple[int, int]:
        """
        Find maximum DPI of an image/PDF and return the number of pages in it.

        :param file: The path to the image/PDf.
        :param default_density: The default max DPI value.
        :return: The DPI and the number of pages in the file.
        """
        density_stdout, _ = self.run_process("identify", "-format", r"%x,%y\n", file)
        density: int = default_density
        pages: int = 0

        for density_line in density_stdout.strip().splitlines():
            pages += 1
            density_x, _, density_y = density_line.strip().partition(",")
            density_page: int = max(int(density_x), int(density_y), 0)
            if density_page > density:
                density = density_page

        return density, pages

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
        args: list[str] = []

        if output == "tif":
            args.extend(("-compress", "LZW", "-depth", "16", "-coalesce"))
        if output == "pdf":
            args.extend(("-coalesce",))

        with TempDir(output_dir) as tmp_dir:
            self.run_process(
                self.dependencies["imagemagick"][0],
                self.file.get_absolute_path(),
                *args,
                dest_file.name,
                cwd=tmp_dir,
            )
            dest_dir.mkdir(parents=True, exist_ok=True)
            tmp_dir.joinpath(dest_file.name).replace(dest_file)

        return [dest_file]


class ConverterPDFToImage(ConverterImage):
    tool_names: ClassVar[list[str]] = ["pdf"]

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = self.output_file(dest_dir, output)
        args: list[str] = []

        if output in ("tif", "tiff"):
            args = ["-compress", "LZW", "-depth", "16"]

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


class ConverterPDFLargeToImage(ConverterImage):
    tool_names: ClassVar[list[str]] = ["pdf-large"]
    outputs: ClassVar[list[str]] = ["tif", "tiff"]

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = self.output_file(dest_dir, output)

        density, pages = self.image_dpi(self.file.get_absolute_path())
        density *= 2

        with TempDir(output_dir) as tmp_dir:
            page_files: list[str] = []

            for page in range(pages):
                page_files.append(f"{tmp_dir.name}-{page:06d}.jpg")
                self.run_process(
                    self.dependencies["imagemagick"][0],
                    "-density",
                    density,
                    "-background",
                    "white",
                    f"{self.file.get_absolute_path()}[{page}]",
                    page_files[-1],
                    cwd=tmp_dir,
                )

            self.run_process(
                self.dependencies["imagemagick"][0],
                "-density",
                density,
                "-compress",
                "LZW",
                "-depth",
                "16",
                f"{tmp_dir.name}-*.jpg",
                dest_file.name,
                cwd=tmp_dir,
            )

            dest_dir.mkdir(parents=True, exist_ok=True)

            return [tmp_dir.joinpath(dest_file.name).replace(dest_file)]


class ConverterTextToImage(ConverterImage):
    tool_names: ClassVar[list[str]] = [
        "text",
        "text-to-image",
    ]

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = self.output_file(dest_dir, output)
        text: str = self.file.get_absolute_path().read_text((self.file.encoding or {}).get("encoding")).strip()
        width: int = max(800, *(len(line) * 10 for line in text.splitlines()), 0)
        height: int = max(600, (text.count("\n") + 1) * 25)
        args: list[str] = []

        if output == "tif":
            args.extend(("-compress", "LZW"))

        with TempDir(output_dir) as tmp_dir:
            self.run_process(
                self.dependencies["imagemagick"][0],
                "-depth",
                "1",
                "-density",
                200,
                *args,
                "-size",
                f"{width}x{height}",
                "xc:black",
                "-fill",
                "white",
                "-pointsize",
                "20",
                "-annotate",
                "+5+45",
                text,
                dest_file.name,
                cwd=tmp_dir,
            )
            dest_dir.mkdir(parents=True, exist_ok=True)
            tmp_dir.joinpath(dest_file.name).replace(dest_file)

        return [dest_file]
