from abc import ABC
from abc import abstractmethod
from os import PathLike
from pathlib import Path
from subprocess import CalledProcessError
from typing import ClassVar

from acacore.database import FileDB
from acacore.models.file import File

from convertool.util import run_process

from .exceptions import ConvertError
from .exceptions import OutputDirError
from .exceptions import OutputExtensionError


class Converter(ABC):
    tool_names: ClassVar[list[str]]
    outputs: ClassVar[list[str]]

    def __init__(
        self,
        file: File,
        database: FileDB | None = None,
        root: Path | None = None,
    ):
        self.file: File = file
        self.database: FileDB | None = database
        self.file.root = self.file.root or root

    def run_process(self, *args: str | int | PathLike, cwd: Path | None = None) -> tuple[str, str]:
        """

        :param args: The arguments for ``subprocess.run``. Non-string arguments are cast to string.
        :param cwd: Optionally, the working directory to use.
        :raise ConvertError: If the process exists with a non-zero code.
        :return: A tuple with the captured stdout and stderr outputs in string format.
        """
        try:
            return run_process(*args, cwd=cwd)
        except CalledProcessError as err:
            raise ConvertError(
                self.file,
                err.stderr or err.stdout or f"An unknown error occurred. Return code {err.returncode}",
            )

    def output_dir(self, output_dir: Path, keep_relative_path: bool = True) -> Path:
        """
        Compute the output directory and check if it is a valid directory path.

        :param output_dir: The base output path.
        :param keep_relative_path: ``True`` if the output path should include the file's parent directories relative to
            its root.
        :raise OutputDirError: If the path already exists and is not a directory.
        :return: The path to the output directory.
        """
        dest_dir: Path = output_dir.joinpath(self.file.relative_path.parent) if keep_relative_path else output_dir
        if dest_dir.exists() and not dest_dir.is_dir():
            raise OutputDirError(self.file, FileExistsError(dest_dir))
        return dest_dir

    def output(self, output: str) -> str:
        """
        Get the normalized output extension and check if it is valid.

        :param output: The desired output extension.
        :raise OutputExtensionError: If ``output`` is not part of the converter's outputs list.
        :return: The normalized output extension.
        """
        if output := next((o for o in self.outputs if o.lower() == output.lower()), None):
            return output
        raise OutputExtensionError(self.file, f"Unsupported output {output}")

    def output_file(self, output_dir: Path, output: str, *, append: bool = False) -> Path:
        """
        :param output_dir: The path to the output directory.
        :param output: The desired output extension.
        :param append: ``True`` if the extension should be appended to the file name instead of replacing the existing
            suffix(es).
        :return: The path to the putput file.
        """
        if append:
            return output_dir / (self.file.name + f".{output}")
        return output_dir / (self.file.name.removesuffix(self.file.suffixes) + f".{output}")

    @abstractmethod
    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]: ...
