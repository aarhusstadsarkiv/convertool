from pathlib import Path
from typing import ClassVar
from zipfile import ZipFile

from convertool.util import TempDir

from .base import ConverterABC
from .base import hashed_file_name
from .exceptions import BadOption
from .exceptions import ConvertError


class ZIPFileConverter(ConverterABC):
    name: ClassVar[str] = "zipfile"
    outputs: ClassVar[list[str]] = ["file"]

    def test_options(self):
        if "path" not in self.options:
            raise BadOption(self.file, "Missing 'path' option.")

    def output_filename(self, output: str, *, append: bool = False) -> str:
        if self.hashed_output_name:
            return hashed_file_name(self.file.get_absolute_path() / self.options["path"])
        return Path(self.options["path"]).name

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = dest_dir.joinpath(self.output_filename(output))

        with TempDir(self.root) as tmp_dir:
            with ZipFile(self.file.get_absolute_path()) as zf:
                try:
                    member = zf.getinfo(self.options["path"])
                except KeyError:
                    raise ConvertError(self.file, f"{self.options['path']!r} is not in ZIP file.")

                if member.is_dir():
                    raise ConvertError(self.file, f"{self.options['path']!r} is a directory.")

                tmp_file = Path(zf.extract(member, tmp_dir))

            return [tmp_file.replace(dest_file)]
