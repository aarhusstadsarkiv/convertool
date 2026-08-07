from pathlib import Path
from subprocess import CalledProcessError
from typing import ClassVar

from convertool.util import TempDir

from .base import ConverterABC
from .exceptions import ConvertError


class VectorConverter(ConverterABC):
    name: ClassVar[str] = "vector"
    outputs: ClassVar[list[str]] = ["pdf"]
    dependencies: ClassVar[dict[str, list[str]]] = {"chromium": ["chromium", "chromium-browser", "google-chrome"]}
    process_timeout: ClassVar[int] = 60

    @classmethod
    def output_name(cls, output: str) -> str:
        return "pdf"

    def output_extension(self, output: str) -> str:
        return ".pdf"

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        self.test_output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = dest_dir.joinpath(self.output_file(output))

        with TempDir(output_dir) as tmp_dir:
            tmp_file = tmp_dir.joinpath("output.pdf")

            [_, _, process_result] = self.run_process(
                self.dependencies["chromium"][0],
                "--headless",
                "--no-sandbox",
                f"--print-to-pdf={tmp_file}",
                "--no-pdf-header-footer",
                self.file.get_absolute_path(),
                cwd=tmp_dir,
            )

            if not tmp_file.is_file():
                raise ConvertError(
                    self.file,
                    "Output file not found.",
                    CalledProcessError(
                        process_result.returncode,
                        process_result.args,
                        process_result.stdout,
                        process_result.stderr,
                    ),
                )

            dest_dir.mkdir(parents=True, exist_ok=True)

            tmp_file.replace(dest_file)

        return [dest_file]
