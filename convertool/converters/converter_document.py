from functools import lru_cache
from pathlib import Path
from typing import ClassVar

from acacore.utils.functions import rm_tree

from .base import _test_dependency
from .base import ConverterABC


class ConverterDocument(ConverterABC):
    tool_names: ClassVar[list[str]] = ["document"]
    outputs: ClassVar[list[str]] = ["odt", "pdf", "html"]
    process_timeout: ClassVar[float] = 60.0

    @classmethod
    def dependencies(cls):
        _test_dependency("libreoffice", "--version")

    # noinspection PyMethodMayBeStatic
    def output_filter(self, output: str) -> str:  # noqa: ARG002
        return ""

    # noinspection DuplicatedCode
    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)
        output_filter: str = self.output_filter(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path)
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
            return [f.replace(dest_dir / f.name) for f in dest_dir_tmp.iterdir() if f.is_file()]
        finally:
            rm_tree(dest_dir_tmp)
