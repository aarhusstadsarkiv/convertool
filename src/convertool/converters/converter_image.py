from pathlib import Path
from typing import ClassVar

from convertool.util import TempDir

from .base import ConverterABC
from .exceptions import BadOption


class ConverterImage(ConverterABC):
    tool_names: ClassVar[list[str]] = ["image"]
    outputs: ClassVar[list[str]] = [
        "jpg",
        "jpeg",
        "jp2",
        "png",
        "tif",
        "tiff",
    ]
    process_timeout: ClassVar[float] = 180.0
    dependencies: ClassVar[dict[str, list[str]]] = {"nconvert": ["nconvert"], "imagemagick": ["magick", "convert"]}

    def test_options(self):
        if (v := self.options.get("program")) not in ("nconvert", "imagemagick", None):
            raise BadOption(f"Invalid value {v!r} for 'program' option.")
        if (v := self.options.get("layers")) not in ("true", True, None):
            raise BadOption(f"Invalid value {v!r} for 'layers' option.")

    def output(self, output: str) -> str:
        if output == "jpeg":
            output = "jpg"
        elif output == "tiff":
            output = "tif"
        return super().output(output)

    def image_dpi(self, file: Path, default_density: int = 150) -> tuple[int, int]:
        """
        Find maximum DPI of an image/PDF and return the number of pages in it.

        :param file: The path to the image/PDf.
        :param default_density: The default max DPI value.
        :return: The DPI and the number of pages in the file.
        """
        density_stdout, *_ = self.run_process("identify", "-format", r"%x,%y\n", file)
        density: int = default_density
        pages: int = 0

        for density_line in density_stdout.strip().splitlines():
            pages += 1
            density_x, _, density_y = density_line.strip().partition(",")
            density_page: int = max(int(density_x), int(density_y), 0)
            if density_page > density:
                density = density_page

        return density, pages

    def convert_imagemagick(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = self.output_file(dest_dir, output)
        args: list[str] = []
        filename: Path = self.file.get_absolute_path()

        if self.options.get("layers") in ("true", True):
            filename = filename.with_name(filename.name + "[0]")
            args.extend(("-background", "none", "-flatten"))
        if output == "tif":
            args.extend(("-compress", "LZW", "-depth", "16"))

        with TempDir(output_dir) as tmp_dir:
            self.run_process(
                self.dependencies["imagemagick"][0],
                filename,
                *args,
                dest_file.name,
                cwd=tmp_dir,
            )
            dest_dir.mkdir(parents=True, exist_ok=True)
            tmp_dir.joinpath(dest_file.name).replace(dest_file)

        return [dest_file]

    def convert_nconvert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = self.output_file(dest_dir, output)
        args: list[str] = []

        if output in ("jpg", "jpeg"):
            args.extend(["-out", "jpeg", "-xall", "-o", "out-#"])
        elif output == "png":
            args.extend(["-out", "png", "-xall", "-o", "out-#"])
        elif output == "jp2":
            args.extend(["-out", "jp2", "-xall", "-o", "out-#"])
        elif output in ("tif", "tiff"):
            args.extend(["-out", "tiff", "-xall", "-multi", "-c", "2", "-o", "out"])
        else:
            args.extend(["-out", output, "-xall", "-o", "out"])

        with TempDir(output_dir) as tmp_dir:
            self.run_process(
                self.dependencies["nconvert"][0],
                *args,
                "-dpi",
                200,
                self.file.get_absolute_path(),
                cwd=tmp_dir,
            )

            dest_dir.mkdir(parents=True, exist_ok=True)

            return [
                f.replace(dest_dir.joinpath(dest_file.stem + f.name.removeprefix("out")))
                for f in sorted(tmp_dir.iterdir())
                if f.is_file()
            ]

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        if self.options.get("program") == "imagemagick":
            return self.convert_imagemagick(output_dir, output, keep_relative_path=keep_relative_path)
        else:
            return self.convert_nconvert(output_dir, output, keep_relative_path=keep_relative_path)
