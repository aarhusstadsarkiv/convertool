from pathlib import Path
from typing import ClassVar

from convertool.util import TempDir

from .base import _hashed_file_name
from .base import _shared_dependencies
from .base import _shared_platforms
from .base import _shared_process_timeout
from .base import ConverterABC
from .base import dummy_base_file
from .converter_pdf import ConverterPDFToImage


class ConverterCAD(ConverterABC):
    tool_names: ClassVar[list[str]] = ["cad", "emf"]
    outputs: ClassVar[list[str]] = ["dxf", "pdf", "svg"]
    process_timeout: ClassVar[float] = 120
    platforms: ClassVar[list[str]] = ["win32"]
    dependencies: ClassVar[dict[str, list[str]]] = {"abviewer": ["ABViewer"]}

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        output_files: list[Path] = []

        with TempDir(output_dir) as tmp_dir:
            self.run_process(
                self.dependencies["abviewer"][0],
                "/c",
                output,
                f"dir={tmp_dir}",
                self.file.get_absolute_path(),
            )
            dest_dir.mkdir(parents=True, exist_ok=True)

            for f in tmp_dir.iterdir():
                if not f.is_file():
                    continue
                if self.hashed_output_name:
                    output_files.append(f.replace(dest_dir / _hashed_file_name(self.file.relative_path / f.name)))
                else:
                    output_files.append(f.replace(dest_dir / f.name))

        return output_files


class ConverterCADToImage(ConverterABC):
    tool_names: ClassVar[list[str]] = ConverterCAD.tool_names
    outputs: ClassVar[list[str]] = ConverterPDFToImage.outputs
    platforms: ClassVar[list[str] | None] = _shared_platforms(ConverterCAD, ConverterPDFToImage)
    dependencies: ClassVar[dict[str, list[str]] | None] = _shared_dependencies(ConverterCAD, ConverterPDFToImage)
    process_timeout: ClassVar[float | None] = _shared_process_timeout(ConverterCAD, ConverterPDFToImage)

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)

        with TempDir(output_dir) as tmp_dir:
            pdfs = ConverterCAD(
                self.file,
                self.root,
                self.relative_root,
                self.database,
                timeout=self.timeout,
                hashed_output_name=self.hashed_output_name,
            ).convert(tmp_dir, "pdf")
            if not pdfs:
                return []

            pdf = pdfs[0]

            return ConverterPDFToImage(
                dummy_base_file(pdf, tmp_dir),
                tmp_dir,
                tmp_dir,
                self.database,
                timeout=self.timeout,
                hashed_output_name=self.hashed_output_name,
            ).convert(
                output_dir,
                output,
                keep_relative_path=keep_relative_path,
            )
