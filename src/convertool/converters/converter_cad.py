from pathlib import Path
from typing import ClassVar
from xml.sax.saxutils import escape

from convertool.util import TempDir

from .base import ConverterABC
from .base import hashed_file_name
from .exceptions import ConvertError


def export_xml(file: str | Path, output_extension: str, dest_file: str | Path) -> str:
    xml: list[str] = [
        '<?xml version="1.0" encoding="utf-8"?>',
        '<cadsofttools version="2">',
        f'<load file="{escape(str(file))}"/>',
    ]

    if output_extension == ".dxf":
        xml.extend(
            [
                "<save>",
                f'<ExportParams FileName="{escape(str(Path(dest_file).with_suffix("")))}" Format="{escape(output_extension)}">',
                "<Version>AutoCAD2000</Version>",
                "<IsConvertImageToOLE>true</IsConvertImageToOLE>",
                "</ExportParams>",
                "</save>",
            ]
        )
    elif output_extension == ".pdf":
        xml.extend(
            [
                "<save>",
                f'<ExportParams FileName="{escape(str(Path(dest_file).with_suffix("")))}" Format="{escape(output_extension)}">',
                "</ExportParams>",
                "</save>",
            ]
        )
    elif output_extension == ".svg":
        xml.extend(
            [
                "<save>",
                f'<ExportParams FileName="{escape(str(Path(dest_file).with_suffix("")))}" Format="{escape(output_extension)}">',
                "</ExportParams>",
                "</save>",
            ]
        )
    else:
        raise NotImplementedError(output_extension)

    xml.append("</cadsofttools>")

    return "\n".join(xml)


class CADConverter(ConverterABC):
    name: ClassVar[str] = "cad"
    outputs: ClassVar[list[str]] = ["dxf", "pdf", "svg"]
    process_timeout: ClassVar[float] = 120
    use_process: ClassVar[bool] = True
    platforms: ClassVar[list[str]] = ["win32"]
    dependencies: ClassVar[dict[str, list[str]]] = {"abviewer": ["ABViewer"]}

    @classmethod
    def output_name(cls, output: str) -> str:
        if output == "dxf":
            return "cad"
        if output == "pdf":
            return "pdf"
        if output == "svg":
            return "vector"
        return output

    def output_extension(self, output: str) -> str:
        if output == "dxf":
            return ".dxf"
        if output == "pdf":
            return ".pdf"
        if output == "svg":
            return ".svg"
        return f".{output}"

    def output_puid(self, output: str) -> str | None:
        if output == "svg":
            return "fmt/413"
        return None

    def converter(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        self.test_output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        output_files: list[Path] = []

        with TempDir(output_dir) as tmp_dir:
            tmp_file = tmp_dir.joinpath("output").with_suffix(self.output_extension(output))
            cmd_file = tmp_dir.joinpath("export.xml")
            cmd_file.write_text(export_xml(self.file.get_absolute_path(), tmp_file.suffix, tmp_file), "utf-8")

            _, _, process = self.run_process(self.dependencies["abviewer"][0], "-processxml", cmd_file)

            dest_dir.mkdir(parents=True, exist_ok=True)

            for f in tmp_dir.iterdir():
                if not f.is_file():
                    continue
                if f == cmd_file:
                    continue
                if self.hashed_output_name:
                    output_files.append(f.replace(dest_dir / hashed_file_name(self.file.relative_path / f.name)))
                else:
                    output_files.append(f.replace(dest_dir / f.name))

            if not output_files:
                raise ConvertError(self.file, "No output files found.", process)

        return output_files
