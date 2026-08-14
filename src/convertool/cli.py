from collections.abc import Callable
from datetime import datetime
from json import JSONDecodeError
from json import loads
from logging import ERROR
from logging import INFO
from logging import WARNING
from pathlib import Path
from shutil import copy2
from traceback import format_tb
from typing import Literal

import structlog
from acacore.__version__ import __version__ as __acacore_version__
from acacore.database import FilesDB
from acacore.database.query import QueryToken
from acacore.database.query import tokens_to_where
from acacore.database.table import Table
from acacore.models.event import Event
from acacore.models.file import BaseFile
from acacore.models.file import ConvertedFile
from acacore.models.file import MasterFile
from acacore.models.file import OriginalFile
from acacore.utils.click import end_program
from acacore.utils.click import param_callback_query
from acacore.utils.click import start_program
from acacore.utils.helpers import ExceptionManager
from click import argument
from click import BadParameter
from click import Choice
from click import Context
from click import group
from click import IntRange
from click import option
from click import pass_context
from click import Path as ClickPath
from click import version_option

from .__version__ import __version__
from .convert import convert_file
from .convert import convert_master_file
from .convert import convert_original_file
from .converters import converters
from .converters import ConvertersGraph
from .converters.exceptions import ConvertError
from .converters.exceptions import MissingDependency
from .converters.exceptions import UnsupportedPlatform
from .util import ctx_params
from .util import get_avid
from .util import open_database


def compile_convert_targets(
    database: FilesDB,
    target: Literal["original:master", "master:access", "master:statutory"],
    query: list[QueryToken],
) -> Table[OriginalFile | MasterFile]:
    src_table: Table[OriginalFile | MasterFile]
    src_query: str

    if target == "original:master":
        src_table = database.original_files
        src_query = "action in ('convert', 'ignore') and processed is false"
    elif target == "master:access":
        src_table = database.master_files
        src_query = "convert_access is not null and processed & 1 = 0"
    elif target == "master:statutory":
        src_table = database.master_files
        src_query = "convert_statutory is not null and processed & 2 = 0"
    else:
        raise ValueError(f"Unsupported file and destination combination: {target}")

    where, params = tokens_to_where(query)

    if where:
        where = f"({where}) and ({src_query})"
    else:
        where, params = src_query, []

    to_process_table: Table[OriginalFile | MasterFile] = database.create_table(
        src_table.model,
        "_convertool",
        [pk.name for pk in src_table.primary_keys],
        {idx: [c.name for c in cs] for idx, cs in src_table.indices.items()},
        ["root"],
        temporary=True,
        exist_ok=False,
    )
    database.execute(
        f"""
                insert into {to_process_table.name}
                select {",".join(to_process_table.columns.keys())} from {src_table.name}
                where {where or "true"}
                """,
        params,
    )
    database.commit()

    return to_process_table


@group("convertool", no_args_is_help=True)
@version_option(__version__, message=f"%(prog)s, version %(version)s\nacacore, version {__acacore_version__}")
def app():
    """Convert files either by themselves or by following the instructions in a digiarch database."""


@app.command("digiarch", no_args_is_help=True, short_help="Convert files from digiarch")
@argument(
    "avid_dir",
    type=ClickPath(exists=True, file_okay=False, writable=True, resolve_path=True),
    required=True,
)
@argument("target", type=Choice(["original:master", "master:access", "master:statutory"]), required=True)
@argument(
    "query",
    nargs=1,
    required=False,
    callback=param_callback_query(
        False,
        "uuid",
        [
            "action",
            "action_data",
            "checksum",
            "convert_access",
            "convert_statutory",
            "encoding",
            "lock",
            "processed",
            "puid",
            "relative_path",
            "signature",
            "uuid",
            "warning",
        ],
        ["warning", "encoding", "action_data", "convert_access", "convert_statutory"],
    ),
)
@option(
    "--tool-include",
    metavar="TOOL",
    type=str,
    multiple=True,
    help="Include only specific tools.  [multiple]",
    callback=lambda _c, _p, v: list(v),
)
@option(
    "--tool-exclude",
    metavar="TOOL",
    type=str,
    multiple=True,
    help="Exclude specific tools.  [multiple]",
    callback=lambda _c, _p, v: list(v),
)
@option("--timeout", metavar="SECONDS", type=IntRange(min=0), default=None, help="Override converters' timeout.")
@option(
    "--commit",
    metavar="INTEGER",
    type=IntRange(0),
    default=1,
    show_default=True,
    help="Number of files edited per commit.",
)
@option(
    "--hashed-names/--no-hashed-names",
    is_flag=True,
    default=True,
    show_default=True,
    help="Use hashed names instead of filenames.",
)
@option(
    "--keep-temporary-files",
    is_flag=True,
    default=False,
    help="Keep temporary files and folders created by each converter.",
)
@option("--show-disabled-converters", is_flag=True, default=False, help="Show converters that are not available.")
@option("--dry-run", is_flag=True, default=False, help="Show changes without committing them.")
@option("--backup/--no-backup", is_flag=True, default=False, help="Create a backup of the database at start.")
@option("--verbose", is_flag=True, default=False, help="Show all outputs from converters.")
@pass_context
def cmd_digiarch(
    ctx: Context,
    avid_dir: str,
    target: Literal["original:master", "master:access", "master:statutory"],
    query: list[QueryToken],
    tool_include: list[str],
    tool_exclude: list[str],
    timeout: int | None,
    commit: int,
    hashed_names: bool,
    keep_temporary_files: bool,
    show_disabled_converters: bool,
    dry_run: bool,
    backup: bool,
    verbose: bool,
):
    """
    Convert files contained in a digiarch database.

    To convert original files to master files, use the "original:master" TARGET.

    To convert master files to access files, use the "master:access" TARGET.

    To convert master files to statutory files, use the "master:statutory" TARGET.

    The QUERY argument allows to restrict which files will be converted. For details on its usage see the
    "digiarch edit" command.

    The default behaviour is to used MD5 checksums as output names based on the relative path of the source file to avoid collisions.
    To use the original names with new suffixes, use the --no-hashed-names option.

    To restrict the tools that should be used for conversion, use the --tool-exclude and --tool-include options.
    The former will skip files whose tools are in the list, the second will skip files whose tools are not in the list.

    Use the --timeout option to override the converters' timeout, set to 0 to disable timeouts altogether.

    Use the --commit option to change the number of files to be processed for each commit.
    To avoid committing changes until all files have been processed, use 0 as value.

    Use the --verbose option to print the standard output from the converters. The output (standard or error) is always
    printed in case of an error.

    Use the --dry-run option to list files that would be converted without performing any action.

    Use the --backup option to create a backup of the database when the program starts, the backup file will have the
    same stem with the current date and time as suffix.
    """
    avid = get_avid(ctx, avid_dir, "avid_dir")
    committer: Callable[[FilesDB, int], FilesDB | None]
    graph = ConvertersGraph.from_conversers(converters)
    total_files: int = 0
    converted_files: int = 0
    errors: list[BaseException] = []
    uncaught_exceptions: list[BaseException] = []

    with open_database(ctx, avid, "avid_dir") as database:
        logger, _ = start_program(ctx, database, __version__, dry_run)

        if show_disabled_converters:
            graph.filter_conversion_graph(
                on_invalid=lambda p, r: Event.from_command(ctx, "converter.disabled", None).log(
                    WARNING,
                    logger,
                    path=str(p),
                    reason=r,
                )
            )
        else:
            graph.filter_conversion_graph()

        if backup and not dry_run:
            backup_path: Path = avid.database_path.with_name(f"{datetime.now():%Y%m%d%H%M%S}-{avid.database_path.name}")
            Event.from_command(ctx, "backup:start").log(INFO, logger, name=backup_path.name)
            backup_path.unlink(missing_ok=True)
            copy2(avid.database_path, backup_path)
            Event.from_command(ctx, "backup:complete").log(INFO, logger, name=backup_path.name)

        with ExceptionManager(BaseException) as exception:
            Event.from_command(ctx, "compiling:start").log(INFO, logger)

            if commit <= 0:
                committer = lambda _, __: None  # noqa: E731
            elif commit == 1:
                committer = lambda _db, _: _db.commit()  # noqa: E731
            else:
                committer = lambda _db, _n: _db.commit() if _n % commit == 0 else None  # noqa: E731

            to_process_table = compile_convert_targets(database, target, query)

            Event.from_command(ctx, "compiling:end").log(INFO, logger)

            for n, file in enumerate(to_process_table):
                total_files += 1
                output_files: list[ConvertedFile] | None
                src_table: Table[OriginalFile | MasterFile]
                out_table: Table[ConvertedFile]

                with ExceptionManager(BaseException, allow=[KeyboardInterrupt]) as convert_exception:
                    if isinstance(file, OriginalFile):
                        if file.processed:
                            continue

                        output_files = convert_original_file(
                            ctx,
                            avid,
                            database,
                            file,
                            logger,
                            graph,
                            timeout,
                            not verbose,
                            hashed_names,
                            keep_temporary_files,
                            dry_run,
                            tool_include,
                            tool_exclude,
                        )
                        file.processed = True
                        src_table = database.original_files
                        out_table = database.master_files
                    elif isinstance(file, MasterFile) and target == "master:access":
                        if file.processed & 0b01:
                            continue

                        output_files = convert_master_file(
                            ctx,
                            avid,
                            database,
                            file,
                            "access",
                            graph,
                            logger,
                            timeout,
                            not verbose,
                            hashed_names,
                            keep_temporary_files,
                            dry_run,
                            tool_include,
                            tool_exclude,
                        )
                        file.processed = file.processed | 0b01
                        src_table = database.master_files
                        out_table = database.access_files
                    elif isinstance(file, MasterFile) and target == "master:statutory":
                        if file.processed & 0b10:
                            continue

                        output_files = convert_master_file(
                            ctx,
                            avid,
                            database,
                            file,
                            "statutory",
                            graph,
                            logger,
                            timeout,
                            not verbose,
                            hashed_names,
                            keep_temporary_files,
                            dry_run,
                            tool_include,
                            tool_exclude,
                        )
                        file.processed = file.processed | 0b10
                        src_table = database.master_files
                        out_table = database.statutory_files
                    else:
                        raise TypeError(f"Unknown file type {file.__class__}")

                if convert_exception.exception:
                    errors.append(convert_exception.exception)

                    error_event = Event.from_command(
                        ctx,
                        "error",
                        file,
                        reason="".join(format_tb(exception.traceback))
                        if exception.traceback
                        else convert_exception.exception.__class__.__name__,
                    )

                    if isinstance(convert_exception.exception, ConvertError):
                        error_event.data = {"msg": convert_exception.exception.msg}
                        if convert_exception.exception.process and (
                            stdout := convert_exception.exception.process.stdout
                        ):
                            error_event.data["stdout"] = stdout if isinstance(stdout, str) else stdout.decode()
                        elif convert_exception.exception.process and (
                            stderr := convert_exception.exception.process.stderr
                        ):
                            error_event.data["stderr"] = stderr if isinstance(stderr, str) else stderr.decode()
                        error_event.log(ERROR, logger, show_args=["uuid", "data"])
                    else:
                        error_event.log(ERROR, logger, show_args=["uuid", "reason"], exc_info=exception.exception)
                        uncaught_exceptions.append(convert_exception.exception)

                    if not dry_run:
                        database.log.insert(error_event)
                        committer(database, n)

                    continue

                if not output_files:
                    if not dry_run:
                        Event.from_command(ctx, "skipped", file).log(INFO, logger)
                        committer(database, n)
                    continue

                for output_file in output_files:
                    Event.from_command(ctx, "out", output_file).log(INFO, logger)
                    out_table.insert(output_file, on_exists="error")

                src_table.update(file)
                database.log.insert(Event.from_command(ctx, "converted", file, {"files": len(output_files)}))

                converted_files += 1

                committer(database, n)

        Event.from_command(ctx, "summary.files", None).log(INFO, logger, total=total_files)
        Event.from_command(ctx, "summary.files.converted", None).log(INFO, logger, total=converted_files)

        if errors:
            Event.from_command(ctx, "summary.errors", None).log(ERROR, logger, errors=len(errors))

        if uncaught_exceptions:
            Event.from_command(ctx, "summary.errors.unknown", None).log(
                ERROR,
                logger,
                errors=len(errors),
                exceptions=sorted({e.__class__.__name__ for e in uncaught_exceptions}),
            )

        end_program(ctx, database, exception, dry_run, logger)


@app.command("standalone", no_args_is_help=True, short_help="Convert single files.")
@argument("tool", nargs=1)
@argument("output", nargs=1)
@argument("destination", nargs=1, type=ClickPath(file_okay=False, writable=True, resolve_path=True))
@argument(
    "files_paths",
    metavar="FILE...",
    nargs=-1,
    type=ClickPath(exists=True, dir_okay=False, readable=True, resolve_path=True),
    required=True,
)
@option("--via", "via_arg", type=str, multiple=True, help="Specify steps to include in the conversion path.")
@option(
    "--option",
    "-o",
    "options",
    metavar="<TOOL KEY VALUE>",
    type=(str, str, str),
    multiple=True,
    help="Pass options to the converters.",
)
@option("--timeout", metavar="SECONDS", type=IntRange(min=0), default=None, help="Override converters' timeout.")
@option("--verbose", is_flag=True, default=False, help="Show all outputs from converters.")
@option(
    "--root",
    type=ClickPath(file_okay=False, writable=True, resolve_path=True),
    default=None,
    help="Set a root for the given files to keep the relative paths in the output.",
)
@option(
    "--keep-temporary-files",
    is_flag=True,
    default=False,
    help="Keep temporary files and folders created by each converter.",
)
@pass_context
def cmd_standalone(
    ctx: Context,
    tool: str,
    output: str,
    destination: str,
    files_paths: tuple[str, ...],
    via_arg: tuple[str, ...],
    options: tuple[tuple[str, str, str], ...],
    timeout: int | None,
    verbose: bool,
    root: str | None,
    keep_temporary_files: bool,
):
    """
    Convert FILEs to OUTPUT with the given TOOL.

    The converted FILEs will be placed in the DESTINATION directory. To maintain the relative paths of the files, use
    the --root option to set their common parent directory.

    The --via option allows to specify tools that must be included in the conversion path. It's value can be the name
    of a tool, a specific tool/output combination in the format "<tool>:<output>", or a specific output in the format
    ":<output>".

    If more than one path matches the given TOOL, OUTPUT, and --via arguments, the shortest one will be used.

    Use --option with TOOL, KEY and VALUE to pass options to a specific TOOL in the conversion path. VALUE must be in
    JSON format.

    Use the --timeout option to override the converters' timeout, set to 0 to disable timeouts altogether.

    Use the --verbose option to print the standard output from the converters. The output (standard or error) is always
    printed in case of an error.
    """
    logger = structlog.stdlib.get_logger()
    graph = ConvertersGraph.from_conversers(converters)
    graph.filter_conversion_graph(requires_database=False, requires_file_classes=[BaseFile])

    if root and any(not Path(f).is_relative_to(root) for f in files_paths):
        raise BadParameter("not a parent path for all files.", ctx, ctx_params(ctx)["root"])

    try:
        options_dict = {}
        for t, k, v in options:
            options_dict[t] = options_dict.get(t, {}) | {k: loads(v)}
    except JSONDecodeError:
        raise BadParameter("invalid JSON", ctx, ctx_params(ctx)["options"])

    via: list[str | tuple[str | None, str]] = [
        v if not (vp := v.partition(":"))[1] else (vp[0] or None, vp[2]) for v in via_arg
    ]

    conversion_path = graph.find(tool, output, via, shortest=True)

    if not conversion_path:
        Event.from_command(ctx, "error", None).log(
            ERROR,
            logger,
            reason="Converter not found",
            tool=tool,
            output=output,
            via=via,
        )
        return

    Event.from_command(ctx, "converter", None).log(INFO, logger, path=str(conversion_path))

    for file in map(Path, files_paths):
        Event.from_command(ctx, "convert", None).log(INFO, logger, file=str(file.relative_to(root) if root else file))
        output_files = convert_file(
            ctx,
            file,
            root,
            destination,
            conversion_path,
            options_dict,
            logger,
            timeout,
            not verbose,
            False,
            keep_temporary_files,
        )

        for output_file in output_files:
            Event.from_command(ctx, "output", None).log(INFO, logger, file=str(output_file.relative_to(destination)))


@app.command("list", help="List available converters and their dependencies.")
@option(
    "--only-available",
    is_flag=True,
    default=False,
    help="Only show converters that can run on this system.",
)
@option(
    "--show-warnings",
    is_flag=True,
    default=False,
    help="Show warnings for converters that cannot run on this system.",
)
@pass_context
def cmd_list(ctx: Context, only_available: bool, show_warnings: bool):
    graph = ConvertersGraph.from_conversers(converters)
    logger = structlog.stdlib.get_logger()

    table: list[tuple[str, str, str, str, str]] = [("Tool", "Output", "Path", "Platform", "Dependencies")]

    for [tool, output], paths in graph.graph.items():
        for path in paths:
            entry = (
                tool,
                output,
                str(path),
                " / ".join(path.platforms or []),
                ", ".join("/".join(d.split("/")[-1] for d in ds) for ds in path.dependencies or []),
            )

            if only_available or show_warnings:
                try:
                    path.test()
                except (MissingDependency, UnsupportedPlatform) as e:
                    if show_warnings:
                        Event.from_command(ctx, "converter.disabled", None).log(
                            WARNING,
                            logger,
                            path=str(path),
                            reason=e,
                        )
                    if only_available:
                        continue

            table.append(entry)

    max_columns = max(map(len, table))
    column_widths = [max(len(r[c]) for r in table) for c in range(max_columns)]

    print("|", " | ".join(table[0][c].ljust(column_widths[c]) for c in range(max_columns)), "|")

    print("|", " | ".join("-" * column_widths[c] for c in range(max_columns)), "|")

    for row in table[1:]:
        print("|", " | ".join(row[c].ljust(column_widths[c]) for c in range(max_columns)), "|")
