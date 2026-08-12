from abc import ABC
from abc import abstractmethod
from functools import lru_cache
from hashlib import md5
from pathlib import Path
from shutil import which
from subprocess import CalledProcessError
from subprocess import CompletedProcess
from subprocess import TimeoutExpired
from sys import platform
from typing import Any
from typing import ClassVar

from acacore.database import FilesDB
from acacore.models.file import BaseFile
from chardet import DetectionDict

from convertool.util import run_process

from .exceptions import BadFile
from .exceptions import ConvertError
from .exceptions import ConvertTimeoutError
from .exceptions import MissingDependency
from .exceptions import OutputDirError
from .exceptions import UnsupportedOutput
from .exceptions import UnsupportedPlatform


@lru_cache
def test_dependency(*commands: str) -> str:
    for command in commands:
        # noinspection deprecation
        if command_path := which(command):
            return command_path

    raise MissingDependency(commands)


@lru_cache
def test_platforms(*platforms: str):
    if platforms and platform not in platforms:
        raise UnsupportedPlatform(platform, f"Not one of {set(platforms)}.")


def hashed_file_name(path: str | Path) -> str:
    return md5(str(path).encode("utf-8")).hexdigest() + dummy_base_file(path).suffixes


def dummy_base_file(path: str | Path, root: str | Path | None = None) -> BaseFile:
    return BaseFile(
        checksum="",
        encoding=None,
        relative_path=(p := Path(path)).relative_to(root or p.parent),
        is_binary=True,
        size=1,
        puid=None,
        signature=None,
        root=Path(root) if root else p.parent,
    )


class ConverterABC(ABC):
    name: ClassVar[str]
    outputs: ClassVar[list[str]]
    process_timeout: ClassVar[int | float | None] = None
    platforms: ClassVar[list[str] | None] = None
    dependencies: ClassVar[dict[str, list[str]] | None] = None
    multithreading: ClassVar[bool] = False
    requires_file_classes: ClassVar[list[type[BaseFile]]] = [BaseFile]
    requires_database: ClassVar[bool] = False

    def __init__(
        self,
        file: BaseFile,
        root: Path,
        relative_root: Path | None = None,
        database: FilesDB | None = None,
        options: dict[str, Any] | None = None,
        *,
        timeout: int | None = None,
        capture_output: bool = True,
        hashed_output_name: bool = True,
    ) -> None:
        self.test_platforms()
        self.test_dependencies()
        self.file: BaseFile = file
        self.database: FilesDB | None = database
        self.root: Path = root
        self.relative_root: Path = relative_root or root
        self.file.root = root
        self.options: dict[str, Any] = options or {}
        self.capture_output: bool = capture_output
        self.hashed_output_name: bool = hashed_output_name
        self.timeout: int | None = timeout

        if self.requires_file_classes and type(self.file) not in self.requires_file_classes:
            raise BadFile(f"File is not of class {self.requires_file_classes}")

        if self.requires_database and self.database is None:
            raise BadFile("Database is not provided")

        self.test_options()

    @classmethod
    def match_tool(cls, tool: str, output: str) -> bool:
        return tool == cls.name and output in cls.outputs

    @classmethod
    @lru_cache
    def test(cls):
        """
        Test dependencies and platforms.

        :raise UnsupportedPlatform: If the platform is not supported.
        :raise MissingDependency: If a dependency is missing.
        """
        cls.test_platforms()
        cls.test_dependencies()

    @classmethod
    @lru_cache
    def test_platforms(cls):
        """
        Test whether the converter supports the current platform.

        :raise UnsupportedPlatform: If the platform is not supported.
        """
        test_platforms(*cls.platforms or [])

    @classmethod
    @lru_cache
    def test_dependencies(cls):
        """
        Test whether all the converter's dependencies are available.

        :raise MissingDependency: If a dependency is missing.
        """
        dependencies: dict[str, list[str]] = {}
        for dependency, commands in (cls.dependencies or {}).items():
            dependencies[dependency] = [test_dependency(*commands)]
        cls.dependencies = dependencies

    @classmethod
    @lru_cache
    def test_output(cls, output: str):
        """
        Test whether an output is supported by the converter.

        :param output: The output.
        :raise OutputExtensionError: If ``output`` is not part of the converter's outputs list.
        """
        if not any(o.lower() == output.lower() for o in cls.outputs):
            raise UnsupportedOutput(output)

    def test_options(self):
        """
        Test whether the given options are valid.

        :raise BadOption: If the given options are invalid.
        """

    def run_process(
        self,
        command: str,
        *args: str | int | Path,
        cwd: str | Path | None = None,
    ) -> tuple[str, str, CompletedProcess[str]]:
        """
        Run process and capture output.

        If a ``CalledProcessError`` is raised, it is converted to ``ConvertError``.

        :param command: The command to run.
        :param args: The arguments for the given command. Non-string arguments are cast to string.
        :param cwd: Optionally, the working directory to use.
        :raise ConvertError: If the process exists with a non-zero code.
        :raise ConvertTimeoutError: If the process times out.
        :return: A tuple with the captured stdout and stderr outputs in string format.
        """
        try:
            return run_process(
                command,
                *args,
                cwd=cwd,
                capture_output=self.capture_output,
                timeout=self.process_timeout
                if self.timeout is None or self.process_timeout is None
                else (self.timeout or None),
            )
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
        dest_dir: Path = (
            output_dir.joinpath(self.file.get_absolute_path(self.root).relative_to(self.relative_root).parent)
            if keep_relative_path
            else output_dir
        )
        if dest_dir.exists() and not dest_dir.is_dir():
            raise OutputDirError(self.file, FileExistsError(dest_dir))
        if mkdir:
            dest_dir.mkdir(parents=True, exist_ok=True)
        return dest_dir

    @classmethod
    def output_name(cls, output: str) -> str:
        """
        Get the name of a given output.

        :param output: The output.
        :return: The name of the output.
        """
        return output

    def output_extension(self, output: str) -> str:
        """
        Get the extension for a given output.

        :param output: The output.
        :return: The extension.
        """
        return f".{output}"

    # noinspection unused-parameter
    def output_puid(self, output: str) -> str | None:
        """
        Get the PUID for a given output, if available.

        :param output: The output value.
        :return: A PUID if available, else ``None``.
        """
        return None

    # noinspection unused-parameter
    def output_encoding(self, output: str) -> DetectionDict | None:
        """
        Get the encoding for a given output, if available.

        :param output: The output value.
        :return: A ``chardet.DetectionDict`` if available, else ``None``.
        """
        return None

    def output_filename(self, output: str, *, append: bool = False) -> str:
        """
        Get the name of the output file.

        :param output: The desired output.
        :param append: ``True`` if the extension should be appended to the file name instead of replacing the existing
            suffix(es).
        :return: The path to the putput file.
        """
        extension: str = self.output_extension(output)
        name: str = (
            hashed_file_name(self.file.get_absolute_path(self.root).relative_to(self.relative_root))
            if self.hashed_output_name
            else self.file.name
        )

        if not extension:
            return name

        if append:
            return f"{name}.{extension}"

        return f"{name.removesuffix(self.file.suffixes)}{extension}"

    @abstractmethod
    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]: ...


class ConvertersEdge:
    def __init__(self, converter: type[ConverterABC], output: str) -> None:
        self.converter: type[ConverterABC] = converter
        self.output: str = output

    @property
    def name(self):
        return self.converter.name

    def __repr__(self) -> str:
        return f"{self.converter.name}({self.output})"

    def __hash__(self) -> int:
        return hash((self.converter.name, self.output))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ConvertersEdge):
            return self.converter.__class__ is other.converter.__class__ and self.output == other.output
        return False

    def __ne__(self, other: object) -> bool:
        return not (self == other)

    def __add__(self, other: "ConvertersEdge") -> "ConvertersPath":
        return ConvertersPath(self.converter.name, other.output, [self, other])


class ConvertersPath:
    def __init__(self, name: str, output: str, branch: list[ConvertersEdge]) -> None:
        self.name: str = name
        self.output: str = output
        self.branch: list[ConvertersEdge] = branch

    def __repr__(self) -> str:
        return " -> ".join(map(repr, self.branch))

    def __hash__(self) -> int:
        return hash(tuple(self.branch))

    def __len__(self) -> int:
        return len(self.branch)

    def __getitem__(self, item: int) -> ConvertersEdge:
        return self.branch[item]

    def test(self):
        for c in self.branch:
            c.converter.test()
