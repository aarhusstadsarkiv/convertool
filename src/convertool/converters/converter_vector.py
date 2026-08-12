from pathlib import Path
from typing import ClassVar

from convertool.util import TempDir

from .base import ConverterABC
from .exceptions import MissingDependency

try:
    import weasyprint

    weasyprint_error: Exception | None = None
except (ImportError, OSError) as e:
    weasyprint = None
    weasyprint_error: Exception | None = e


class VectorConverter(ConverterABC):
    name: ClassVar[str] = "vector"
    outputs: ClassVar[list[str]] = ["pdf"]

    @classmethod
    def test_dependencies(cls):
        if weasyprint is None:
            raise MissingDependency(["weasyprint"], weasyprint_error or "missing system dependencies")
        super().test_dependencies()

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        self.test_output(output)

        if weasyprint is None:
            raise MissingDependency(["weasyprint"], weasyprint_error or "missing system dependencies")

        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = dest_dir.joinpath(self.output_file(output))

        with TempDir(output_dir) as tmp_dir:
            html = weasyprint.HTML(
                filename=self.file.get_absolute_path(),
                encoding=(self.file.encoding["encoding"] or "") if self.file.encoding else "",
            )

            html.write_pdf(tmp_file := tmp_dir.joinpath(dest_file.name))

            dest_dir.mkdir(parents=True, exist_ok=True)

            tmp_file.replace(dest_file)

        return [dest_file]
