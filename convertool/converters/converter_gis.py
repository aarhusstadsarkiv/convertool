from pathlib import Path
from typing import ClassVar

from acacore.utils.functions import rm_tree

from convertool.converters import ConverterABC
from convertool.converters.base import _test_dependency
from convertool.converters.exceptions import MissingDependency


class ConverterGIS(ConverterABC):
    tool_names: ClassVar[list[str]] = ["gis"]
    outputs: ClassVar[list[str]] = ["gml"]
    process_timeout: ClassVar[float] = 120
    platforms: ClassVar[list[str]] = ["linux"]

    @classmethod
    def dependencies(cls):
        try:
            _test_dependency("which", "ogr2ogr")
        except MissingDependency:
            raise MissingDependency("ogr2ogr")

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path)
        dest_file: Path = self.output_file(dest_dir, output)

        dest_dir_tmp: Path = dest_dir / f"_{dest_file.name}.gis"

        rm_tree(dest_dir_tmp)
        dest_dir_tmp.mkdir(parents=True, exist_ok=True)

        try:
            self.run_process(
                "ogr2ogr",
                "-of",
                "GML",
                "-dsco",
                "FORMAT=GML3",
                dest_dir_tmp / dest_file.name,
                self.file.get_absolute_path(),
            )

            return [f.replace(dest_dir / f.name) for f in dest_dir_tmp.iterdir() if f.is_file()]
        finally:
            rm_tree(dest_dir_tmp)
