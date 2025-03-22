from abc import ABC
from abc import abstractmethod
from functools import lru_cache
from functools import reduce
from os import PathLike
from pathlib import Path
from subprocess import CalledProcessError
from subprocess import TimeoutExpired
from sys import platform
from typing import ClassVar

from acacore.database import FilesDB
from acacore.models.file import BaseFile

from convertool.util import run_process

from .exceptions import ConvertError
from .exceptions import ConvertTimeoutError
from .exceptions import MissingDependency
from .exceptions import OutputDirError
from .exceptions import OutputTargetError
from .exceptions import UnsupportedPlatform


@lru_cache
def _test_dependency(command: str):
    try:
        if platform == "win32":
            run_process("Get-Command", command)
        elif platform in ("linux", "darwin"):
            run_process("which", command)
    except CalledProcessError:
        raise MissingDependency(command)


@lru_cache
def _test_platform(*platforms: str):
    if platforms and platform not in platforms:
        raise UnsupportedPlatform(platform, f"Not one of {platforms}")


def _shared_platforms(*converters: type["ConverterABC"]) -> list[str]:
    platforms: list[list[str]] = [c.platforms for c in converters if c.platforms]

    if not platforms:
        return []

    return list(reduce(lambda a, c: a.union(set(c)), platforms[1:], set(platforms[0]))) or ["no-platform"]


def _shared_dependencies(*converters: type["ConverterABC"]) -> list[str] | None:
    dependencies: list[str] = [d for c in converters for d in c.dependencies or []]
    return sorted(set(dependencies), key=dependencies.index) or None


def _shared_process_timeout(*converters: type["ConverterABC"]) -> float | None:
    return max([c.process_timeout or 0.0 for c in converters], default=0.0) or None


class ConverterABC(ABC):
    tool_names: ClassVar[list[str]]
    outputs: ClassVar[list[str]]
    process_timeout: ClassVar[float | None] = None
    platforms: ClassVar[list[str] | None] = None
    dependencies: ClassVar[list[str] | None] = None

    def __init__(
        self,
        file: BaseFile,
        database: FilesDB | None = None,
        root: Path | None = None,
        *,
        capture_output: bool = True,
    ) -> None:
        self.test_platforms()
        self.test_dependencies()
        self.file: BaseFile = file
        self.database: FilesDB | None = database
        self.file.root = self.file.root or root
        self.capture_output: bool = capture_output

    @classmethod
    def match_tool(cls, tool: str, output: str) -> bool:
        return tool in cls.tool_names and output in cls.outputs

    @classmethod
    @lru_cache
    def test_platforms(cls):
        """
        Test whether the converter supports the current platform.

        :raise UnsupportedPlatform: If the platform is not supported.
        """
        _test_platform(*cls.platforms or [])

    @classmethod
    @lru_cache
    def test_dependencies(cls):
        """
        Test whether all the converter's dependencies are available.

        :raise MissingDependency: If a dependency is missing.
        """
        for dependency in cls.dependencies or []:
            _test_dependency(dependency)

    def run_process(self, *args: str | int | PathLike, cwd: str | PathLike | None = None) -> tuple[str, str]:
        """
        Run process and capture output.

        If a ``CalledProcessError`` is raised, it is converted to ``ConvertError``.

        :param args: The arguments for ``subprocess.run``. Non-string arguments are cast to string.
        :param cwd: Optionally, the working directory to use.
        :raise ConvertError: If the process exists with a non-zero code.
        :raise ConvertTimeoutError: If the process times out.
        :return: A tuple with the captured stdout and stderr outputs in string format.
        """
        try:
            return run_process(*args, cwd=cwd, capture_output=self.capture_output, timeout=self.process_timeout)
        except TimeoutExpired as err:
            raise ConvertTimeoutError(self.file, f"The process timed out after {err.timeout}s", err)
        except CalledProcessError as err:
            raise ConvertError(
                self.file,
                err.stderr or err.stdout or f"An unknown error occurred. Return code {err.returncode}",
                err,
            )

    def output_dir(self, output_dir: Path, *, keep_relative_path: bool = True, mkdir: bool = False) -> Path:
        """
        Compute the output directory and check if it is a valid directory path.

        :param output_dir: The base output path.
        :param keep_relative_path: ``True`` if the output path should include the file's parent directories relative to
            its root.
        :param mkdir: ``True`` if the output directory should be created.
        :raise OutputDirError: If the path already exists and is not a directory.
        :return: The path to the output directory.
        """
        dest_dir: Path = output_dir.joinpath(self.file.relative_path.parent) if keep_relative_path else output_dir
        if dest_dir.exists() and not dest_dir.is_dir():
            raise OutputDirError(self.file, FileExistsError(dest_dir))
        if mkdir:
            dest_dir.mkdir(parents=True, exist_ok=True)
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
        raise OutputTargetError(self.file, f"Unsupported output {output}")

    def output_file(self, output_dir: Path, output: str, *, append: bool = False) -> Path:
        """
        Get the path to the output file.

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
