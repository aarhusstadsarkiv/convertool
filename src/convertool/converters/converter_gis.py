from pathlib import Path
from typing import ClassVar

from convertool.converters import ConverterABC
from convertool.util import TempDir


class ConverterGIS(ConverterABC):
    tool_names: ClassVar[list[str]] = ["gis"]
    outputs: ClassVar[list[str]] = ["gml"]
    process_timeout: ClassVar[float] = 120
    platforms: ClassVar[list[str]] = ["linux"]
    dependencies: ClassVar[dict[str, list[str]]] = {"ogr2ogr": ["ogr2ogr"]}

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = self.output_file(dest_dir, output)

        with TempDir(output_dir) as tmp_dir:
            self.run_process(
                self.dependencies["ogr2ogr"][0],
                "-of",
                "GML",
                "-dsco",
                "FORMAT=GML3",
                dest_file.name,
                self.file.get_absolute_path(),
                cwd=tmp_dir,
            )

            return [f.replace(dest_dir / f.name) for f in tmp_dir.iterdir() if f.is_file()]
