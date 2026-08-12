from pathlib import Path
from typing import ClassVar

from chardet import DetectionDict

from convertool.util import TempDir

from .base import ConverterABC
from .converter_document import DocumentConverter
from .exceptions import BadOption


class TextConverter(ConverterABC):
    name: ClassVar[str] = "text"
    outputs: ClassVar[list[str]] = ["txt"]

    @classmethod
    def output_name(cls, output: str) -> str:
        return "text"

    def output_extension(self, output: str) -> str:
        return ".txt"

    def output_puid(self, output: str) -> str | None:
        if output == "txt":
            return "x-fmt/111"
        return None

    def output_encoding(self, output: str) -> DetectionDict | None:
        if output == "txt":
            return DetectionDict(encoding="utf-8", confidence=1.0, language=None, mime_type="text/plain")
        return None

    def test_options(self):
        if self.options.get("stripnull") not in (None, True, False):
            raise BadOption(f"Invalid value {self.options.get('stripnull')!r} for 'stripnull' option")

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        self.test_output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = dest_dir.joinpath(self.output_file(output))

        text: str = self.file.get_absolute_path().read_text((self.file.encoding or {}).get("encoding")).strip()

        if self.options.get("stripnull") is not False:
            text = text.encode().translate(None, bytes([0])).decode()

        with TempDir(output_dir) as tmp_dir:
            tmp_file = tmp_dir.joinpath(dest_file.name)
            tmp_file.write_text(text, encoding="utf-8")
            dest_dir.mkdir(parents=True, exist_ok=True)
            return [tmp_file.replace(dest_file)]


class TextToDocumentConverter(DocumentConverter):
    name: ClassVar[str] = "text"
