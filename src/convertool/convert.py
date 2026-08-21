from dataclasses import dataclass
from logging import INFO
from pathlib import Path
from typing import Any
from typing import Literal
from typing import overload

from acacore.database import FilesDB
from acacore.models.event import Event
from acacore.models.file import AccessFile
from acacore.models.file import BaseFile
from acacore.models.file import ConvertedFile
from acacore.models.file import MasterFile
from acacore.models.file import OriginalFile
from acacore.models.file import StatutoryFile
from chardet import DetectionDict
from click import Context
from structlog.stdlib import BoundLogger

from .converters import converters as converters_list
from .converters import ConvertersGraph
from .converters import ConvertersPath
from .converters import dummy_base_file
from .converters.exceptions import ConverterNotFound
from .converters.exceptions import ConvertError
from .util import AVID


@dataclass
class ConvertResult[F: BaseFile, R: ConvertedFile]:
    file: F
    converter: ConvertersPath | None = None
    files: list[R] | None = None
    message: str | None = None


def edge_logger(
    ctx: Context | str,
    operation: str,
    logger: BoundLogger,
    file: OriginalFile | MasterFile | None,
    path: ConvertersPath,
    n: int,
):
    # noinspection bad-argument-type
    Event.from_command(ctx, operation, file).log(
        INFO,
        logger,
        converter=path[n].name,
        output=path[n].output,
        step=n + 1,
    )


def convert_original_file(
    __graph: ConvertersGraph | None,
    ctx: Context,
    avid: AVID,
    database: FilesDB,
    file: OriginalFile,
    logger: BoundLogger,
    timeout: int | None = None,
    capture_output: bool = True,
    hashed_output_name: bool = True,
    keep_temporary_files: bool = False,
    dry_run: bool = False,
    tool_include: list[str] | None = None,
    tool_exclude: list[str] | None = None,
) -> ConvertResult[OriginalFile, MasterFile]:
    if file.processed:
        return ConvertResult(file, message="File is already processed")

    tool: str
    output: str
    via: list[str | tuple[str | None, str]] | None = None
    options: dict[str, dict[str, Any]] | None = None

    if file.action == "ignore":
        if not file.action_data.ignore:
            raise ConvertError(file, "Missing ignore action data")
        tool, output = "template", file.action_data.ignore.template
    elif file.action == "convert":
        if not file.action_data.convert:
            raise ConvertError(file, "Missing convert action data")
        tool, output, options, via = (
            file.action_data.convert.tool,
            file.action_data.convert.output,
            file.action_data.convert.options,
            file.action_data.convert.via,
        )
    else:
        raise ConvertError(file, f"File with {file.action!r} cannot be converted.")

    if tool_include and tool not in tool_include:
        return ConvertResult(file, message=f"Tool {tool!r} is not included")
    if tool_exclude and tool in tool_exclude:
        return ConvertResult(file, message=f"Tool {tool!r} is excluded")

    if __graph:
        conversion_path = __graph.find(tool, output, via, shortest=True)
    else:
        conversion_path = (
            ConvertersGraph.from_conversers(converters_list)
            .filter_conversion_graph()
            .find(tool, output, via, shortest=True)
        )

    if not conversion_path:
        raise ConverterNotFound(tool, output, via)

    if dry_run:
        return ConvertResult(file, conversion_path)

    output_paths, converters = conversion_path(
        file,
        avid.path,
        avid.dirs.master_documents,
        avid.dirs.original_documents,
        database,
        options,
        on_edge=lambda p, n: edge_logger(ctx, "step", logger, file, p, n),
        timeout=timeout,
        capture_output=capture_output,
        hashed_output_name=hashed_output_name,
        keep_temporary_files=keep_temporary_files,
    )

    output_files: list[MasterFile] = []

    for i, path in enumerate(output_paths):
        puid: str | None = None
        encoding: DetectionDict | None = None
        if path.suffix == output_paths[0].suffix:
            puid = converters[-1][1].output_puid(converters[-1][0].output)
            encoding = converters[-1][1].output_encoding(converters[-1][0].output)

        output_file = MasterFile.from_file(
            path,
            avid.path,
            {"original_uuid": file.uuid, "sequence": i},
            encoding=encoding["encoding"] if encoding else None,
        )
        output_file.puid = puid

    return ConvertResult(file, conversion_path, output_files)


@overload
def convert_master_file(
    __graph: ConvertersGraph | None,
    ctx: Context,
    avid: AVID,
    database: FilesDB,
    file: MasterFile,
    target: Literal["statutory"],
    logger: BoundLogger,
    timeout: int | None = None,
    capture_output: bool = True,
    hashed_output_name: bool = True,
    keep_temporary_files: bool = False,
    dry_run: bool = False,
    tool_include: list[str] | None = None,
    tool_exclude: list[str] | None = None,
) -> ConvertResult[MasterFile, StatutoryFile]: ...


@overload
def convert_master_file(
    __graph: ConvertersGraph | None,
    ctx: Context,
    avid: AVID,
    database: FilesDB,
    file: MasterFile,
    target: Literal["access"],
    logger: BoundLogger,
    timeout: int | None = None,
    capture_output: bool = True,
    hashed_output_name: bool = True,
    keep_temporary_files: bool = False,
    dry_run: bool = False,
    tool_include: list[str] | None = None,
    tool_exclude: list[str] | None = None,
) -> ConvertResult[MasterFile, AccessFile]: ...


def convert_master_file(
    __graph: ConvertersGraph | None,
    ctx: Context,
    avid: AVID,
    database: FilesDB,
    file: MasterFile,
    target: Literal["statutory", "access"],
    logger: BoundLogger,
    timeout: int | None = None,
    capture_output: bool = True,
    hashed_output_name: bool = True,
    keep_temporary_files: bool = False,
    dry_run: bool = False,
    tool_include: list[str] | None = None,
    tool_exclude: list[str] | None = None,
) -> ConvertResult[MasterFile, StatutoryFile | AccessFile]:
    if target == "access" and file.processed & 0b01:
        return ConvertResult(file, message="File is already processed")
    if target == "statutory" and file.processed & 0b10:
        return ConvertResult(file, message="File is already processed")

    tool: str
    output: str
    via: list[str | tuple[str | None, str]] | None
    options: dict[str, dict[str, Any]] | None
    output_dir: Path
    output_cls: type[StatutoryFile] | type[AccessFile]

    if target == "statutory":
        if not file.convert_statutory:
            raise ConvertError(file, "Missing statutory convert data")
        tool, output, options, via = (
            file.convert_statutory.tool,
            file.convert_statutory.output,
            file.convert_statutory.options,
            file.convert_statutory.via,
        )
        output_dir = avid.dirs.documents
        output_cls = StatutoryFile
    elif target == "access":
        if not file.convert_access:
            raise ConvertError(file, "Missing access convert data")
        tool, output, options, via = (
            file.convert_access.tool,
            file.convert_access.output,
            file.convert_access.options,
            file.convert_access.via,
        )
        output_dir = avid.dirs.access_documents
        output_cls = AccessFile
    else:
        raise ValueError(f"Unknown target {target!r}")

    if tool_include and tool not in tool_include:
        return ConvertResult(file, message=f"Tool {tool!r} is not included")
    if tool_exclude and tool in tool_exclude:
        return ConvertResult(file, message=f"Tool {tool!r} is excluded")

    if __graph:
        conversion_path = __graph.find(tool, output, via, shortest=True)
    else:
        conversion_path = (
            ConvertersGraph.from_conversers(converters_list)
            .filter_conversion_graph()
            .find(tool, output, via, shortest=True)
        )

    if not conversion_path:
        raise ConverterNotFound(tool, output, via)

    if dry_run:
        return ConvertResult(file, conversion_path)

    output_paths, converters = conversion_path(
        file,
        avid.path,
        output_dir,
        avid.dirs.master_documents,
        database,
        options,
        on_edge=lambda p, n: edge_logger(ctx, "step", logger, file, p, n),
        timeout=timeout,
        capture_output=capture_output,
        hashed_output_name=hashed_output_name,
        keep_temporary_files=keep_temporary_files,
    )

    output_files: list[ConvertedFile] = []

    for i, path in enumerate(output_paths):
        puid: str | None = None
        encoding: DetectionDict | None = None
        if path.suffix == output_paths[0].suffix:
            puid = converters[-1][1].output_puid(converters[-1][0].output)
            encoding = converters[-1][1].output_encoding(converters[-1][0].output)

        output_file = output_cls.from_file(
            path,
            avid.path,
            {"original_uuid": file.uuid, "sequence": i},
            encoding=encoding["encoding"] if encoding else None,
        )
        output_file.puid = puid

    # noinspection bad-return
    return ConvertResult(file, conversion_path, output_files)


def convert_file(
    ctx: Context | str,
    path: Path,
    root: str | Path | None,
    output_dir: str | Path,
    conversion: ConvertersPath | tuple[ConvertersGraph, str, str, list[str | tuple[str | None, str]] | None],
    options: dict[str, dict[str, Any]] | None,
    logger: BoundLogger,
    timeout: int | None = None,
    capture_output: bool = True,
    hashed_output_name: bool = False,
    keep_temporary_files: bool = False,
) -> list[Path]:
    path = path.absolute()
    file = dummy_base_file(path, root or path.root)

    if isinstance(conversion, tuple):
        graph, tool, output, via = conversion
        conversion_path = (
            ConvertersGraph(graph.graph)
            .filter_conversion_graph(requires_database=False, requires_file_classes=[BaseFile])
            .find(tool, output, via, shortest=True)
        )

        if not conversion_path:
            raise ConverterNotFound(tool, output, via)
    else:
        conversion_path = conversion

    output_paths, _ = conversion_path(
        file,
        root or path.root,
        output_dir,
        root,
        None,
        options,
        on_edge=lambda p, n: edge_logger(ctx, "step", logger, None, p, n),
        timeout=timeout,
        capture_output=capture_output,
        hashed_output_name=hashed_output_name,
        keep_temporary_files=keep_temporary_files,
        keep_relative_path=root is not None,
    )

    return output_paths
