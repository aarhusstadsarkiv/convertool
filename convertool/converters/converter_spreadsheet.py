from pathlib import Path
from typing import ClassVar

from acacore.utils.functions import rm_tree

from .base import Converter
from .exceptions import ConvertError


class ConverterDocument(Converter):
    tool_names: ClassVar[list[str]] = ["spreadsheet"]
    outputs: ClassVar[list[str]] = ["ods", "pdf", "html"]

    # noinspection PyMethodMayBeStatic
    def output_filter(self, output: str) -> str:
        return ""

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)
        output_filter: str = self.output_filter(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path)
        dest_file: Path = self.output_file(dest_dir, output)
        dest_dir_tmp: Path = dest_dir.joinpath(f"_tmp_{self.file.uuid}")
        rm_tree(dest_dir_tmp)
        dest_dir_tmp.mkdir(parents=True, exist_ok=True)

        try:
            self.run_process(
                "libreoffice",
                "--headless",
                "--convert-to",
                f"{output}:{output_filter}" if output_filter else output,
                "--outdir",
                dest_dir_tmp,
                self.file.get_absolute_path(),
            )
            dest_file_tmp: Path | None = next(f for f in dest_dir_tmp.iterdir() if f.is_file())
            if dest_file_tmp is None:
                raise ConvertError(self.file, "Could not find converted file.")
            dest_file_tmp.replace(dest_file)
            return [dest_file]
        finally:
            rm_tree(dest_dir_tmp)
