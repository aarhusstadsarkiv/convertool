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

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:  # noqa: ARG002
        if "path" not in self.options:
            raise BadOption(self.file, "Missing 'path' option.")

        target_file: Path = Path(self.options["path"])

        if target_file.is_absolute():
            raise BadOption(self.file, "Absolute paths are not supported.")

        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = self.output_file(dest_dir, target_file.suffix.lstrip("."))

        with TempDir(self.file.root) as tmp_dir:
            with ZipFile(self.file.get_absolute_path()) as zf:
                try:
                    tmp_file = Path(zf.extract(str(target_file), tmp_dir))
                except KeyError:
                    raise ConvertError(self.file, f"{target_file} is not in ZIP file.")

            return [tmp_file.replace(dest_file)]
