from pathlib import Path
from typing import ClassVar
from zipfile import ZipFile

from convertool.util import TempDir

from .base import _hashed_file_name
from .base import ConverterABC
from .base import dummy_base_file
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

    def output_file(self, output_dir: Path, output: str, *, append: bool = False) -> Path:
        if self.hashed_putput_name:
            return output_dir.joinpath(_hashed_file_name(self.file.get_absolute_path() / self.options["path"]))
        return output_dir.joinpath(Path(self.options["path"]).name)

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:  # noqa: ARG002
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = self.output_file(dest_dir, "")

        with TempDir(self.file.root) as tmp_dir:
            with ZipFile(self.file.get_absolute_path()) as zf:
                try:
                    member = zf.getinfo(self.options["path"])
                except KeyError:
                    raise ConvertError(self.file, f"{self.options['path']!r} is not in ZIP file.")

                if member.is_dir():
                    raise ConvertError(self.file, f"{self.options['path']!r} is a directory.")

                tmp_file = Path(zf.extract(member, tmp_dir))

            return [tmp_file.replace(dest_file)]
