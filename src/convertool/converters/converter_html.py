from pathlib import Path
from types import ModuleType
from typing import ClassVar

from convertool.util import TempDir

from .base import ConverterABC


class HTMLConverter(ConverterABC):
    name: ClassVar[str] = "html"
    outputs: ClassVar[list[str]] = ["pdf", "pdfa-1", "pdfa-2", "pdfa-3", "pdfa-4"]
    process_timeout: ClassVar[int] = 60
    use_process: ClassVar[bool] = True
    dependencies: ClassVar[dict[str, list[str]]] = {"weasyprint": ["weasyprint"]}
    _weasyprint: ModuleType | None = None
    _weasyprint_error: Exception | None = None

    @classmethod
    def _variant(cls, output: str) -> str | None:
        return {
            "pdf": None,
            "pdfa-1": "pdf/a-1b",
            "pdfa-2": "pdf/a-2b",
            "pdfa-3": "pdf/a-3b",
            "pdfa-4": "pdf/a-4f",
        }.get(output)

    def converter(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        self.test_output(output)

        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = dest_dir.joinpath(self.output_filename(output))
        args: list[str] = []

        if variant := self._variant(output):
            args.extend(("--pdf-variant", variant))

        with TempDir(output_dir) as tmp_dir:
            self.run_process(
                self.dependencies["weasyprint"][0],
                *args,
                self.file.get_absolute_path(),
                tmp_file := tmp_dir.joinpath(dest_file.name),
                cwd=tmp_dir,
            )

            dest_dir.mkdir(parents=True, exist_ok=True)

            tmp_file.replace(dest_file)

        return [dest_file]
