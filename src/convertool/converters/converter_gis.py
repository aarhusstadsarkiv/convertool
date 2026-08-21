from pathlib import Path
from shutil import copy2
from typing import ClassVar

from acacore.models.file import OriginalFile
from chardet import DetectionDict

from convertool.util import file_suffixes
from convertool.util import TempDir

from .base import ConverterABC
from .exceptions import BadOption


class GISConverter(ConverterABC):
    name: ClassVar[str] = "gis"
    outputs: ClassVar[list[str]] = ["gml", "gml3", "shp", "geojson"]
    process_timeout: ClassVar[float] = 120
    platforms: ClassVar[list[str]] = ["linux"]
    dependencies: ClassVar[dict[str, list[str]]] = {"ogr2ogr": ["ogr2ogr"]}

    @classmethod
    def output_name(cls, output: str) -> str:
        if output == "gml":
            return "xml"
        if output == "gml3":
            return "xml"
        if output == "shp":
            return "xml"
        if output == "geojson":
            return "text"
        return output

    def output_extension(self, output: str) -> str:
        if output == "gml":
            return ".gml"
        if output == "gml3":
            return ".gml"
        if output == "shp":
            return ".shp"
        if output == "geojson":
            return ".geojson"
        return f".{output}"

    def output_puid(self, output: str) -> str | None:
        if output == "gml":
            return "x-fmt/227"
        if output == "gml3":
            return "fmt/1047"
        if output == "shp":
            return "x-fmt/235"
        if output == "geojson":
            return "fmt/1367"
        return None

    def output_encoding(self, output: str) -> DetectionDict | None:
        if output == "gml":
            return DetectionDict(encoding="utf-8", confidence=1.0, language=None, mime_type="application/gml+xml")
        if output == "gml3":
            return DetectionDict(encoding="utf-8", confidence=1.0, language=None, mime_type="application/gml+xml")
        if output == "shp":
            return DetectionDict(encoding="utf-8", confidence=1.0, language=None, mime_type=None)
        if output == "geojson":
            return DetectionDict(encoding="utf-8", confidence=1.0, language=None, mime_type="application/geo+json")
        return None

    def test_options(self):
        if (iformat := self.options.get("input_format")) is not None and not isinstance(iformat, str):
            raise BadOption(f"Invalid value {iformat!r} for 'input_format' option")

    def assemble(self, tmp_dir: Path) -> list[Path]:
        files: list[Path] = []

        if self.database and isinstance(self.file, OriginalFile) and self.file.gis_main:
            for file in self.database.original_files.select({"gis_main": str(self.file.gis_main)}):
                copy2(
                    file.get_absolute_path(self.root),
                    dest := tmp_dir.joinpath(self.file.stem).with_suffix(file.suffix),
                )
                files.append(dest)
        else:
            file_stem: str = self.file.stem
            for path in self.file.get_absolute_path().parent.iterdir():
                if not path.is_file():
                    continue
                suffixes: str = file_suffixes(path)
                stem: str = path.name.removesuffix(suffixes)
                if stem == file_stem:
                    copy2(path, dest := tmp_dir.joinpath(stem).with_suffix(path.suffix))
                    files.append(dest)

        return files

    def converter(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        self.test_output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = dest_dir.joinpath(self.output_filename(output))
        args: list[str] = []

        if iformat := self.options.get("input_format"):
            args.extend(("-if", str(iformat)))

        if output in ("gml", "gml3"):
            args.extend(("-of", "GML", "-dsco", "FORMAT=GML3"))
        elif output == "shp":
            args.extend(("-of", "ESRI Shapefile"))
        elif output == "geojson":
            args.extend(("-of", "GeoJSON"))

        with (
            TempDir(output_dir) as tmp_filesdir,
            TempDir(output_dir) as tmp_outdir,
        ):
            self.assemble(tmp_filesdir)

            self.run_process(
                self.dependencies["ogr2ogr"][0],
                *args,
                dest_file.name,
                tmp_filesdir.joinpath(self.file.name),
                cwd=tmp_outdir,
            )

            dest_dir.mkdir(parents=True, exist_ok=True)

            return [f.replace(dest_dir / f.name) for f in tmp_outdir.iterdir()]
