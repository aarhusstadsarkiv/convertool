from pathlib import Path
from typing import ClassVar

from convertool.converters import ConverterABC
from convertool.util import TempDir


class ConverterHTML(ConverterABC):
    tool_names: ClassVar[list[str]] = ["html"]
    outputs: ClassVar[list[str]] = ["pdf"]
    dependencies: ClassVar[list[str]] = ["chrome"]
    process_timeout: ClassVar[float] = 60

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = self.output_file(dest_dir, output)

        with TempDir(output_dir) as tmp_dir:
            self.run_process(
                "chrome",
                "--headless",
                "--no-sandbox",
                "--print-to-pdf",
                "--no-pdf-header-footer",
                self.file.get_absolute_path(),
                cwd=tmp_dir,
            )
            dest_dir.mkdir(parents=True, exist_ok=True)
            tmp_dir.joinpath("output.pdf").replace(dest_file)

        return [dest_file]
