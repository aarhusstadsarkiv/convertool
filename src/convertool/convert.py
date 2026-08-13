from logging import ERROR
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

from .converters import ConvertersGraph
from .converters import ConvertersPath
from .converters import dummy_base_file
from .converters.exceptions import ConverterNotFound
from .util import AVID


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
    ctx: Context,
    avid: AVID,
    database: FilesDB,
    file: OriginalFile,
    logger: BoundLogger,
    graph: ConvertersGraph,
    timeout: int | None = None,
    capture_output: bool = True,
    hashed_output_name: bool = True,
    keep_temporary_files: bool = False,
    dry_run: bool = False,
    tool_include: list[str] | None = None,
    tool_exclude: list[str] | None = None,
) -> list[MasterFile] | None:
    if file.processed:
        return None

    tool: str
    output: str
    via: list[str | tuple[str | None, str]] = []
    options: dict[str, dict[str, Any]] = {}

    if file.action == "ignore":
        if not file.action_data.ignore:
            Event.from_command(ctx, "error", file, reason="Missing ignore action data").log(ERROR, logger)
            return None
        tool, output = "template", file.action_data.ignore.template
    elif file.action == "convert":
        if not file.action_data.convert:
            Event.from_command(ctx, "error", file, reason="Missing convert action data").log(ERROR, logger)
            return None
        tool, output = file.action_data.convert.tool, file.action_data.convert.output or file.action_data.convert.tool
    else:
        raise ConverterNotFound(None, None, f"File with {file.action!r} cannot be converted.")

    if tool_include and tool not in tool_include:
        return None
    if tool_exclude and tool in tool_exclude:
        return None

    conversion_path = graph.find(tool, output, via, shortest=True)

    if not conversion_path:
        Event.from_command(ctx, "error", file, reason="Cannot find converter").log(
            ERROR,
            logger,
            tool=tool,
            output=output,
            via=via or None,
        )
        return None

    if dry_run:
        Event.from_command(ctx, "converter", file).log(INFO, logger, path=str(conversion_path))
        return None

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

    return output_files


@overload
def convert_master_file(
    ctx: Context,
    avid: AVID,
    database: FilesDB,
    file: MasterFile,
    target: Literal["statutory"],
    graph: ConvertersGraph,
    logger: BoundLogger,
    timeout: int | None = None,
    capture_output: bool = True,
    hashed_output_name: bool = True,
    keep_temporary_files: bool = False,
    dry_run: bool = False,
    tool_include: list[str] | None = None,
    tool_exclude: list[str] | None = None,
) -> list[StatutoryFile] | None: ...


@overload
def convert_master_file(
    ctx: Context,
    avid: AVID,
    database: FilesDB,
    file: MasterFile,
    target: Literal["access"],
    graph: ConvertersGraph,
    logger: BoundLogger,
    timeout: int | None = None,
    capture_output: bool = True,
    hashed_output_name: bool = True,
    keep_temporary_files: bool = False,
    dry_run: bool = False,
    tool_include: list[str] | None = None,
    tool_exclude: list[str] | None = None,
) -> list[AccessFile] | None: ...


def convert_master_file(
    ctx: Context,
    avid: AVID,
    database: FilesDB,
    file: MasterFile,
    target: Literal["statutory", "access"],
    graph: ConvertersGraph,
    logger: BoundLogger,
    timeout: int | None = None,
    capture_output: bool = True,
    hashed_output_name: bool = True,
    keep_temporary_files: bool = False,
    dry_run: bool = False,
    tool_include: list[str] | None = None,
    tool_exclude: list[str] | None = None,
) -> list[StatutoryFile] | list[AccessFile] | None:
    if file.processed:
        return None

    tool: str
    output: str
    via: list[str | tuple[str | None, str]] = []
    options: dict[str, dict[str, Any]] = {}
    output_dir: Path
    output_cls: type[StatutoryFile] | type[AccessFile]

    if target == "statutory":
        if not file.convert_statutory:
            raise ConverterNotFound(None, None, "Missing statutory convert data")
        tool, output = file.convert_statutory.tool, file.convert_statutory.output or file.convert_statutory.tool
        output_dir = avid.dirs.documents
        output_cls = StatutoryFile
    elif target == "access":
        if not file.convert_access:
            raise ConverterNotFound(None, None, "Missing access convert data")
        tool, output = file.convert_access.tool, file.convert_access.output or file.convert_access.tool
        output_dir = avid.dirs.access_documents
        output_cls = AccessFile
    else:
        raise ValueError(f"Unknown target {target!r}")

    if tool_include and tool not in tool_include:
        return None
    if tool_exclude and tool in tool_exclude:
        return None

    conversion_path = graph.find(tool, output, via, shortest=True)

    if not conversion_path:
        raise ConverterNotFound(tool, output, f"Cannot find converter for {tool}:{output}{f':{via}' if via else ''}")

    if dry_run:
        Event.from_command(ctx, "converter", file).log(INFO, logger, path=str(conversion_path))
        return None

    output_paths, converters = conversion_path(
        file,
        avid.path,
        output_dir,
        avid.dirs.master_documents,
        database,
        options,
        on_edge=lambda n, p: edge_logger(ctx, "step", logger, file, p, n),
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
    return output_files


def convert_file(
    ctx: Context,
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
            raise ConverterNotFound(
                tool,
                output,
                f"Cannot find converter for {tool}:{output}{f':{via}' if via else ''}",
            )
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
