from pathlib import Path
from shutil import copy2
from typing import ClassVar

from acacore.models.file import OriginalFile

from convertool.util import file_suffixes
from convertool.util import TempDir

from .base import ConverterABC
from .exceptions import ConvertError


class ConverterGIS(ConverterABC):
    tool_names: ClassVar[list[str]] = ["gis"]
    outputs: ClassVar[list[str]] = ["gml"]
    process_timeout: ClassVar[float] = 120
    platforms: ClassVar[list[str]] = ["linux"]
    dependencies: ClassVar[dict[str, list[str]]] = {"ogr2ogr": ["ogr2ogr"]}

    def assemble(self, tmp_dir: Path) -> list[Path]:
        files: list[Path] = []

        root: Path | None = self.file.root

        if root is None:
            raise ConvertError(self.file, "File root not set")

        if self.database and isinstance(self.file, OriginalFile) and self.file.gis_main:
            for file in self.database.original_files.select({"gis_main": str(self.file.gis_main)}):
                copy2(file.get_absolute_path(root), dest := tmp_dir.joinpath(self.file.stem).with_suffix(file.suffixes))
                files.append(dest)
        else:
            file_stem: str = self.file.stem
            for path in self.file.get_absolute_path().parent.iterdir():
                if not path.is_file():
                    continue
                suffixes: str = file_suffixes(path)
                stem: str = path.name.removesuffix(suffixes)
                if stem == file_stem:
                    copy2(path, dest := tmp_dir.joinpath(stem).with_suffix(suffixes))
                    files.append(dest)

        return files

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = self.output_file(dest_dir, output)

        with TempDir(output_dir) as tmp_filesdir:
            self.assemble(tmp_filesdir)

            with TempDir(output_dir) as tmp_outdir:
                self.run_process(
                    self.dependencies["ogr2ogr"][0],
                    "-of",
                    "GML",
                    "-dsco",
                    "FORMAT=GML3",
                    dest_file.name,
                    tmp_filesdir.joinpath(self.file.name),
                    cwd=tmp_outdir,
                )

                dest_dir.mkdir(parents=True, exist_ok=True)

                return [f.replace(dest_dir / f.name) for f in tmp_outdir.iterdir()]
