from abc import ABC
from abc import abstractmethod
from collections.abc import Callable
from functools import lru_cache
from functools import reduce
from hashlib import md5
from pathlib import Path
from shutil import which
from subprocess import CalledProcessError
from subprocess import CompletedProcess
from subprocess import TimeoutExpired
from sys import platform
from typing import Any
from typing import ClassVar
from typing import Literal
from typing import overload
from typing import Self
from typing import Union

from acacore.database import FilesDB
from acacore.models.file import BaseFile
from chardet import DetectionDict

from convertool.util import run_process
from convertool.util import TempDir

from .exceptions import BadDatabase
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
    requires_file_classes: ClassVar[list[type[BaseFile]] | None] = None
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
            raise BadFile(file, f"File is not of class {self.requires_file_classes}")

        if self.requires_database and self.database is None:
            raise BadDatabase("Database is not provided")

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
            return f"{name}{extension}"

        return f"{name.removesuffix(self.file.suffixes)}{extension}"

    def read_text(self, encoding: str | None = None) -> str:
        """
        Read text from the file.

        :param encoding: Optionally, the encoding to use. If unset, then the encoding stored in `BaseFile.encoding`
            is used instead.
        :return: The content of the file as a string.
        """
        return self.file.get_absolute_path().read_text(
            encoding or (self.file.encoding["encoding"] if self.file.encoding else None)
        )

    def read_bytes(self) -> bytes:
        """
        Read bytes from the file.

        :return: The content of the file as a string.
        """
        return self.file.get_absolute_path().read_bytes()

    @abstractmethod
    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]: ...


class ConvertersEdge:
    def __init__(self, converter: type[ConverterABC], output: str) -> None:
        self.converter: type[ConverterABC] = converter
        self.output: str = output

    @property
    def name(self) -> str:
        return self.converter.name

    @property
    def dependencies(self) -> dict[str, list[str]] | None:
        return self.converter.dependencies

    @property
    def platforms(self) -> list[str] | None:
        return self.converter.platforms

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
        self.edges: list[ConvertersEdge] = branch

    def __repr__(self) -> str:
        return " -> ".join(map(repr, self.edges))

    def __hash__(self) -> int:
        return hash(tuple(self.edges))

    def __len__(self) -> int:
        return len(self.edges)

    def __getitem__(self, item: int) -> ConvertersEdge:
        return self.edges[item]

    @property
    def dependencies(self) -> list[list[str]] | None:
        return (
            reduce(
                lambda dss, ds: [*dss, _ds] if (_ds := [d for d in ds if not any(d in __ds for __ds in dss)]) else dss,
                [ds for e in self.edges if e.dependencies is not None for ds in e.dependencies.values()],
                [],
            )
            or None
        )

    @property
    def platforms(self) -> list[str] | None:
        platforms = [set(e.platforms) for e in self.edges if e.platforms is not None]
        if platforms:
            return list(reduce(lambda pss, ps: pss & ps, platforms))
        return None

    def test(self):
        for c in self.edges:
            c.converter.test()

    def has_step(self, step: str | tuple[str | None, str]) -> bool:
        if isinstance(step, str):
            return any(e.name == step for e in self.edges)
        if isinstance(step, tuple) and step[0] is None:
            return any(e.output == step[1] for e in self.edges)
        return any(e.name == step[0] and e.output == step[1] for e in self.edges)

    def __call__(
        self,
        file: BaseFile,
        root: str | Path,
        output_dir: str | Path,
        relative_root: str | Path | None = None,
        database: FilesDB | None = None,
        options: dict[str, dict[str, Any]] | None = None,
        *,
        on_edge: Callable[["ConvertersPath", int], None] | None = None,
        timeout: int | None = None,
        capture_output: bool = True,
        hashed_output_name: bool = True,
        keep_relative_path: bool = True,
        keep_temporary_files: bool = False,
    ) -> tuple[list[Path], list[tuple[ConvertersEdge, ConverterABC]]]:
        output_dir = Path(output_dir)
        working_file: BaseFile = file
        working_root: Path = Path(root)
        working_relative_root: Path = Path(relative_root or root)
        working_outputs: list[Path] = []
        outputs: list[Path] = []
        converters: list[tuple[ConvertersEdge, ConverterABC]] = []

        output_dir.mkdir(parents=True, exist_ok=True)

        with TempDir(output_dir, delete=not keep_temporary_files) as temp_dir:
            for n, edge in enumerate(self.edges):
                if on_edge:
                    on_edge(self, n)

                converter = edge.converter(
                    working_file,
                    working_root,
                    working_relative_root,
                    database,
                    options.get(edge.name) if options else None,
                    timeout=timeout,
                    capture_output=capture_output,
                    hashed_output_name=hashed_output_name,
                )

                edge_dir = temp_dir.joinpath(f"{n:02} {edge.name} {edge.output}")
                edge_dir.mkdir(parents=True, exist_ok=True)

                working_outputs = converter.convert(edge_dir, edge.output, keep_relative_path=keep_relative_path)

                working_file = dummy_base_file(working_outputs[0], edge_dir)
                working_root = edge_dir
                working_relative_root = edge_dir
                converters.append((edge, converter))

            for output in working_outputs:
                dest_file = output_dir.joinpath(output.relative_to(working_root))
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                outputs.append(output.replace(dest_file))

        return outputs, converters


class ConvertersGraph:
    def __init__(self, graph: dict[tuple[str, str], list[ConvertersPath]]) -> None:
        self.graph: dict[tuple[str, str], list[ConvertersPath]] = graph

    def __repr__(self) -> str:
        return self.graph.__repr__()

    @overload
    def __getitem__(self, item: tuple[str, str]) -> list[ConvertersPath]: ...

    @overload
    def __getitem__(self, item: slice) -> "ConvertersGraph": ...

    def __getitem__(self, item: tuple[str, str] | slice) -> Union[list[ConvertersPath], "ConvertersGraph"]:
        if isinstance(item, tuple):
            return self.graph[item]

        return self.slice(item.start, item.stop, item.step)

    @overload
    def get[T](self, path: tuple[str, str], default: T) -> list[ConvertersPath] | T: ...

    @overload
    def get(self, path: tuple[str, str], default: None = None) -> list[ConvertersPath] | None: ...

    def get[T](self, path: tuple[str, str], default: T | None = None) -> list[ConvertersPath] | T | None:
        return self.graph.get(path, default)

    def slice(
        self,
        name: str | None = None,
        output: str | None = None,
        step: str | list[str | tuple[str | None, str]] | None = None,
    ) -> "ConvertersGraph":
        steps = step or []
        steps = steps if isinstance(steps, list) else [steps]
        new_graph: dict[tuple[str, str], list[ConvertersPath]] = self.graph

        if name and output and steps:
            new_graph = {
                k: _ps
                for k, ps in self.graph.items()
                if k == (name, output) and (_ps := [p for p in ps if all(p.has_step(s) for s in steps)])
            }
        elif name and output:
            new_graph = {k: ps for k, ps in self.graph.items() if k == (name, output)}
        elif name and steps:
            new_graph = {
                k: _ps
                for k, ps in self.graph.items()
                if k[0] == name and (_ps := [p for p in ps if all(p.has_step(s) for s in steps)])
            }
        elif output and steps:
            new_graph = {
                k: _ps
                for k, ps in self.graph.items()
                if k[1] == output and (_ps := [p for p in ps if all(p.has_step(s) for s in steps)])
            }
        elif name:
            new_graph = {k: ps for k, ps in self.graph.items() if k[0] == name}
        elif output:
            new_graph = {k: ps for k, ps in self.graph.items() if k[1] == output}
        elif steps:
            new_graph = {
                k: _ps for k, ps in self.graph.items() if (_ps := [p for p in ps if all(p.has_step(s) for s in steps)])
            }

        return ConvertersGraph(new_graph)

    @overload
    def find(
        self,
        name: str,
        output: str,
        via: list[str | tuple[str | None, str]] | None = None,
        shortest: Literal[True] = True,
    ) -> ConvertersPath: ...

    @overload
    def find(
        self,
        name: str,
        output: str,
        via: list[str | tuple[str | None, str]] | None = None,
        shortest: Literal[False] = False,
    ) -> list[ConvertersPath]: ...

    def find(
        self,
        name: str,
        output: str,
        via: list[str | tuple[str | None, str]] | None = None,
        shortest: bool = True,
    ) -> ConvertersPath | list[ConvertersPath] | None:
        if not (paths := self.get((name, output))):
            return None

        if via:
            paths = [p for p in paths if all(p.has_step(v) for v in via)]
            if not paths:
                return None

        if shortest:
            return sorted(paths, key=len)[0]

        return paths

    @classmethod
    def from_conversers(cls, converters: list[type[ConverterABC]]) -> "ConvertersGraph":
        def _compute_converter_branches(
            _conv: type[ConverterABC],
            _prev_edges: list[ConvertersEdge] | None = None,
            _prev_platforms: list[str] | None = None,
        ) -> list[ConvertersPath]:
            conv_paths: list[ConvertersPath] = []

            if _conv.platforms and _prev_platforms and not set(_prev_platforms).intersection(_conv.platforms):
                return []

            for output in _conv.outputs:
                edge = ConvertersEdge(_conv, output)

                if _prev_edges and edge in _prev_edges:
                    continue

                conv_paths.append(ConvertersPath(_conv.name, output, [edge]))

                conv_paths.extend(
                    [
                        ConvertersPath(_conv.name, b.output, [edge, *b.edges])
                        for c in converters
                        if (c.requires_file_classes is None or BaseFile in c.requires_file_classes)
                        and (_conv.requires_database or not c.requires_database)
                        and c.name == _conv.output_name(output)
                        for b in _compute_converter_branches(
                            c,
                            [
                                *(_prev_edges or []),
                                *(ConvertersEdge(_conv, _o) for _o in _conv.outputs),
                            ],
                            [
                                *(_prev_platforms or []),
                                *(_conv.platforms or []),
                            ],
                        )
                    ]
                )

            return list(set(conv_paths))

        paths: dict[tuple[str, str], list[ConvertersPath]] = {}

        for conv in converters:
            for path in _compute_converter_branches(conv, []):
                key = (path.name, path.output)
                paths[key] = [*paths.get(key, []), path]

        return ConvertersGraph({(k[0], k[1]): bs for k, bs in paths.items()})

    def filter_conversion_graph(
        self,
        requires_database: bool = True,
        requires_file_classes: list[type[BaseFile]] | None = None,
        on_invalid: Callable[[ConvertersPath, str | Exception], None] | None = None,
    ) -> Self:
        def _test_path(path: ConvertersPath) -> ConvertersPath | None:
            try:
                if requires_database is False and any(e.converter.requires_database for e in path.edges):
                    if on_invalid:
                        on_invalid(path, "Requires database")
                    return None
                if requires_file_classes and not all(
                    not e.converter.requires_file_classes
                    or any(c in e.converter.requires_file_classes for c in requires_file_classes)
                    for e in path.edges
                ):
                    if on_invalid:
                        on_invalid(path, "Requires different classes")
                    return None
                path.test()
                return path
            except (MissingDependency, UnsupportedPlatform) as e:
                if on_invalid:
                    on_invalid(path, e)
                return None

        self.graph = {
            k: _ps for k, ps in self.graph.items() if (_ps := [_p for p in ps if (_p := _test_path(p)) is not None])
        }

        return self
