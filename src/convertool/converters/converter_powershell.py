from abc import ABC
from pathlib import Path
from subprocess import CompletedProcess
from typing import ClassVar

from .base import ConverterABC
from .exceptions import ConvertError
from .resources.scripts import scripts


class PowershellConverterABC(ConverterABC, ABC):
    platforms: ClassVar[list[str]] = ["win32"]
    dependencies: ClassVar[dict[str, list[str]]] = {"powershell": ["powershell"]}

    def run_script(
        self,
        script: str,
        cwd: str | Path | None = None,
        **kwargs: str | int | Path,
    ) -> tuple[str, str, CompletedProcess[str]]:
        if not (script_file := scripts.joinpath(script)).is_file():
            raise ConvertError(self.file, f"Script {script} not found.")

        args: list[str | int | Path] = []
        for key, value in kwargs.items():
            args.append(f"-{key}")
            args.append(value)

        return self.run_process(self.dependencies["powershell"][0], "-file", script_file, *args, cwd=cwd)
