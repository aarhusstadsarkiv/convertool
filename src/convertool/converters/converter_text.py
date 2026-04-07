from pathlib import Path
from typing import ClassVar

from convertool.util import TempDir

from .base import ConverterABC
from .converter_image import ConverterImage
from .exceptions import BadOption


class ConverterText(ConverterABC):
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
            return [tmp_file.replace(dest_file)]


class ConverterTextToImage(ConverterImage):
    tool_names: ClassVar[list[str]] = [
        "text",
        "text-to-image",
    ]

    def test_options(self):
        if self.options.get("stripnull") not in (None, True, False):
            raise BadOption(f"Invalid value {self.options.get('stripnull')!r} for 'stripnull' option")

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = self.output_file(dest_dir, output)
        text: str = self.file.get_absolute_path().read_text((self.file.encoding or {}).get("encoding")).strip()
        if self.options.get("stripnull"):
            text = text.encode().translate(None, bytes([0])).decode()
        width: int = max(800, *(len(line) * 10 for line in text.splitlines()), 0)
        height: int = max(600, (text.count("\n") + 1) * 25)
        args: list[str] = []

        if output == "tif":
            args.extend(("-compress", "LZW"))

        with TempDir(output_dir) as tmp_dir:
            tmp_text_file = tmp_dir.joinpath(f"{dest_file.name}.txt")
            tmp_text_file.write_text(text, encoding="utf-8")
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
                f"@{tmp_text_file.name}",
                dest_file.name,
                cwd=tmp_dir,
            )
            dest_dir.mkdir(parents=True, exist_ok=True)
            tmp_dir.joinpath(dest_file.name).replace(dest_file)

        return [dest_file]
