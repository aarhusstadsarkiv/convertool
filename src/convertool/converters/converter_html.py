from pathlib import Path
from types import ModuleType
from typing import ClassVar

from convertool.util import TempDir

from .base import ConverterABC
from .exceptions import MissingDependency


class HTMLConverter(ConverterABC):
    name: ClassVar[str] = "html"
    outputs: ClassVar[list[str]] = ["pdf", "pdfa-1", "pdfa-2", "pdfa-3", "pdfa-4"]
    _weasyprint: ModuleType | None = None
    _weasyprint_error: Exception | None = None

    @classmethod
    def test_dependencies(cls):
        cls._import_weasyprint()

        if cls._weasyprint is None:
            raise MissingDependency(["weasyprint"], cls._weasyprint_error or "missing system dependencies")

        super().test_dependencies()

    @classmethod
    def _import_weasyprint(cls):
        if cls._weasyprint or cls._weasyprint_error:
            return

        try:
            import weasyprint

            cls._weasyprint = weasyprint
            cls._weasyprint_error = None
        except (ImportError, OSError) as e:
            cls._weasyprint = None
            cls._weasyprint_error = e

    @classmethod
    def _variant(cls, output: str) -> str | None:
        return {
            "pdf": None,
            "pdfa-1": "pdf/a-1b",
            "pdfa-2": "pdf/a-2b",
            "pdfa-3": "pdf/a-3b",
            "pdfa-4": "pdf/a-4f",
        }.get(output)

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        self.test_output(output)

        if self._weasyprint is None:
            raise MissingDependency(["weasyprint"], self._weasyprint_error or "missing system dependencies")

        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = dest_dir.joinpath(self.output_filename(output))

        with TempDir(output_dir) as tmp_dir:
            html = self._weasyprint.HTML(
                filename=self.file.get_absolute_path(),
                encoding=(self.file.encoding["encoding"] or "") if self.file.encoding else "",
            )

            html.write_pdf(tmp_file := tmp_dir.joinpath(dest_file.name), options={"pdf_variant": self._variant(output)})

            dest_dir.mkdir(parents=True, exist_ok=True)

            tmp_file.replace(dest_file)

        return [dest_file]
