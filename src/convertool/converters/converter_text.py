from pathlib import Path
from typing import ClassVar

from convertool.util import TempDir

from .base import ConverterABC
from .exceptions import BadOption


class ConverterText(ConverterABC):
    tool_names: ClassVar[list[str]] = ["text"]
    outputs: ClassVar[list[str]] = ["txt"]

    def test_options(self):
        if self.options.get("stripnull") not in (None, True, False):
            raise BadOption(f"Invalid value {self.options.get('stripnull')!r} for 'stripnull' option")

    def output_puid(self, output: str) -> str | None:
        if output == "txt":
            return "x-fmt/111"
        return None

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = self.output_file(dest_dir, output)
        text: str = self.file.get_absolute_path().read_text((self.file.encoding or {}).get("encoding")).strip()
        if self.options.get("stripnull"):
            text = text.encode().translate(None, bytes([0])).decode()

        with TempDir(output_dir) as tmp_dir:
            tmp_file = tmp_dir.joinpath(dest_file.name)
            tmp_file.write_text(text, encoding="utf-8")
            dest_dir.mkdir(parents=True, exist_ok=True)
            return [tmp_file.replace(dest_file)]


class ConverterTextToImage(ConverterABC):
    tool_names: ClassVar[list[str]] = [
        "text",
        "text-to-image",
    ]
    outputs: ClassVar[list[str]] = [
        "jpg",
        "jpeg",
        "jp2",
        "png",
        "tif",
        "tiff",
    ]
    process_timeout: ClassVar[float] = 180.0
    dependencies: ClassVar[dict[str, list[str]]] = {"imagemagick": ["magick", "convert"]}

    def output(self, output: str) -> str:
        if output == "jpeg":
            output = "jpg"
        elif output == "tiff":
            output = "tif"
        return super().output(output)

    def test_options(self):
        if self.options.get("stripnull") not in (None, True, False):
            raise BadOption(f"Invalid value {self.options.get('stripnull')!r} for 'stripnull' option")
        if font := self.options.get("font"):
            if not isinstance(font, str):
                raise BadOption(f"Invalid value {font!r} for 'font' option")
            if not Path(font).is_file():
                raise BadOption(f"File {font!r} not found for 'font' option")

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = self.output_file(dest_dir, output)
        text: str = self.file.get_absolute_path().read_text((self.file.encoding or {}).get("encoding")).strip()
        if self.options.get("stripnull"):
            text = text.encode().translate(None, bytes([0])).decode()
        width: int = max(800, *(len(line.rstrip()) for line in text.splitlines()), 0)
        args: list[str] = []

        if output == "tif":
            args.extend(("-compress", "LZW"))

        if font := self.options.get("font"):
            args.extend(("-font", str(font)))

        with TempDir(output_dir) as tmp_dir:
            tmp_text_file = tmp_dir.joinpath(f"{dest_file.name}.txt")
            tmp_text_file.write_text(text, encoding="utf-8")
            self.run_process(
                self.dependencies["imagemagick"][0],
                "-background",
                "white",
                "-fill",
                "black",
                "-page",
                "A4",
                "-density",
                200,
                "-units",
                "PixelsPerInch",
                "-pointsize",
                int((width * 2) / 200),
                *args,
                f"text:{tmp_text_file.name}",
                dest_file.name,
                cwd=tmp_dir,
            )
            dest_dir.mkdir(parents=True, exist_ok=True)
            tmp_dir.joinpath(dest_file.name).replace(dest_file)

        return [dest_file]
