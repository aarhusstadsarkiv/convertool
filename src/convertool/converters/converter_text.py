from pathlib import Path
from typing import ClassVar

from convertool.util import TempDir

from . import ConverterDocument
from . import ConverterPDFToImage
from .base import _shared_dependencies
from .base import _shared_process_timeout
from .base import ConverterABC
from .base import dummy_base_file
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
    outputs: ClassVar[list[str]] = ConverterPDFToImage.outputs
    process_timeout: ClassVar[float | None] = _shared_process_timeout(ConverterDocument, ConverterPDFToImage)
    dependencies: ClassVar[dict[str, list[str]] | None] = _shared_dependencies(ConverterDocument, ConverterPDFToImage)
    multithreading: ClassVar[bool] = ConverterDocument.multithreading and ConverterPDFToImage.multithreading

    def test_options(self):
        if self.options.get("stripnull") not in (None, True, False):
            raise BadOption(f"Invalid value {self.options.get('stripnull')!r} for 'stripnull' option")
        if self.options.get("render") not in (None, True, False):
            raise BadOption(f"Invalid value {self.options.get('render')!r} for 'render' option")

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)

        text: str = self.file.get_absolute_path().read_text((self.file.encoding or {}).get("encoding")).strip()

        if self.options.get("stripnull"):
            text = text.encode().translate(None, bytes([0])).decode()

        with TempDir(output_dir) as tmp_dir:
            tmp_text_dir = self.output_dir(tmp_dir, keep_relative_path=keep_relative_path)
            tmp_text_file = tmp_text_dir.joinpath(self.file.name)
            if self.options.get("render") is False:
                tmp_text_file = tmp_text_file.with_suffix(".txt")
            tmp_text_file.parent.mkdir(parents=True, exist_ok=True)
            tmp_text_file.write_text(text, encoding="utf-8")

            if not (
                pdfs := ConverterDocument(
                    dummy_base_file(tmp_text_file, tmp_dir),
                    self.database,
                    tmp_dir,
                    hashed_output_name=self.hashed_output_name,
                ).convert(tmp_dir, "pdf")
            ):
                return []

            tmp_text_file.unlink(missing_ok=True)

            pdf = pdfs[0]

            return ConverterPDFToImage(
                dummy_base_file(pdf, tmp_dir),
                self.database,
                tmp_dir,
                hashed_output_name=self.hashed_output_name,
            ).convert(output_dir, output, keep_relative_path=keep_relative_path)
