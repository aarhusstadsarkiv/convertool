from pathlib import Path
from shutil import copy2
from typing import ClassVar

from chardet import DetectionDict

from convertool.util import TempDir

from .base import ConverterABC
from .base import hashed_file_name


class CopyConverter(ConverterABC):
    name: ClassVar[str] = "copy"
    outputs: ClassVar[list[str]] = ["copy"]

    def output_puid(self, output: str) -> str | None:
        return self.file.puid

    def output_encoding(self, output: str) -> DetectionDict | None:
        return self.file.encoding

    def output_filename(self, output: str, *, append: bool = False) -> str:
        name: str = (
            hashed_file_name(self.file.get_absolute_path(self.root).relative_to(self.relative_root))
            if self.hashed_output_name
            else self.file.name
        )
        return name

    def converter(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path, mkdir=True)
        dest_file: Path = dest_dir.joinpath(self.output_filename(output))

        with TempDir(output_dir) as tmp_dir:
            copy2(self.file.get_absolute_path(), tmp_file := tmp_dir.joinpath(dest_file))
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            tmp_file.replace(dest_file)

        return [dest_file]
