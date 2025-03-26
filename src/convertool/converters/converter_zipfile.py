from pathlib import Path
from typing import ClassVar
from zipfile import ZipFile

from convertool.converters import ConverterABC
from convertool.converters.exceptions import ConvertError
from convertool.util import TempDir


class ConverterZIPFile(ConverterABC):
    tool_names: ClassVar[list[str]] = ["zipfile"]
    outputs: ClassVar[list[str]] = []

    @classmethod
    def match_tool(cls, tool: str, output: str) -> bool:
        return tool in cls.tool_names

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        if "path" not in self.options:
            raise ConvertError(self.file, "Missing 'path' option.")

        target_file: Path = Path(self.options["path"])

        if target_file.is_absolute():
            raise ConvertError(self.file, "Absolute paths are not supported.")

        with TempDir(self.file.root) as tmp_dir:
            with ZipFile(self.file.get_absolute_path()) as zf:
                try:
                    tmp_file = Path(zf.extract(str(target_file), tmp_dir))
                except KeyError:
                    raise ConvertError(self.file, f"{target_file} is not in ZIP file.")

            return [tmp_file.replace(output_dir / target_file.name)]
