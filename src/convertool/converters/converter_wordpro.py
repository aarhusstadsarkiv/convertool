from pathlib import Path
from typing import ClassVar

from convertool.converters.converter_powershell import PowershellConverterABC
from convertool.converters.exceptions import ConvertError
from convertool.util import TempDir


class WordProConverter(PowershellConverterABC):
    name: ClassVar[str] = "wordpro"
    outputs: ClassVar[list[str]] = ["rtf"]
    use_process: ClassVar[bool] = True
    process_timeout: ClassVar[int] = 30
    _scripts: ClassVar[dict[str, str]] = {
        "rtf": "wordpro_lwp2rtf.ps1",
    }

    @classmethod
    def output_name(cls, output: str) -> str:
        if output == "rtf":
            return "document"
        return output

    def output_extension(self, output: str) -> str:
        if output == "rtf":
            return ".rtf"
        return super().output_extension(output)

    def converter(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        self.test_output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = dest_dir.joinpath(self.output_filename(output))
        script: str = self._scripts[output]

        with TempDir(output_dir) as tmp_dir:
            self.run_script(
                script,
                tmp_dir,
                ifile=self.file.get_absolute_path(),
                ofile=(tmp_file := tmp_dir.joinpath(dest_file.name)),
            )

            if not tmp_file.is_file():
                raise ConvertError(self.file, "Output file was not created.")

            dest_file.parent.mkdir(parents=True, exist_ok=True)

            return [tmp_file.replace(dest_file)]
