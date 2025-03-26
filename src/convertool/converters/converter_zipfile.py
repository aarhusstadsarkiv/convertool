from pathlib import Path
from typing import ClassVar
from zipfile import ZipFile

from convertool.util import TempDir

from .base import ConverterABC
from .exceptions import BadOption
from .exceptions import ConvertError


class ConverterZIPFile(ConverterABC):
    tool_names: ClassVar[list[str]] = ["zipfile"]
    outputs: ClassVar[list[str]] = []

    @classmethod
    def match_tool(cls, tool: str, output: str) -> bool:  # noqa: ARG003
        return tool in cls.tool_names

    def test_options(self):
        if "path" not in self.options:
            raise BadOption(self.file, "Missing 'path' option.")

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:  # noqa: ARG002
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = self.output_file(dest_dir, Path(self.options["path"]).suffix.lstrip("."))

        with TempDir(self.file.root) as tmp_dir:
            with ZipFile(self.file.get_absolute_path()) as zf:
                try:
                    tmp_file = Path(zf.extract(self.options["path"], tmp_dir))
                except KeyError:
                    raise ConvertError(self.file, f"{self.options['path']!r} is not in ZIP file.")

            return [tmp_file.replace(dest_file)]
