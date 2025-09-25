from collections.abc import Callable
from datetime import datetime
from itertools import batched
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
from acacore.database.table import Table
from acacore.models.event import Event
from acacore.models.file import AccessFile
from acacore.models.file import ConvertedFile
from acacore.models.file import MasterFile
from acacore.models.file import OriginalFile
from acacore.models.file import StatutoryFile
from acacore.models.reference_files import ActionData
from acacore.models.reference_files import ConvertAction
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
from .convert import convert_async_queue
from .convert import convert_queue
from .convert import ConvertInstructions
from .convert import file_queues
from .convert import master_file_converter
from .convert import original_file_converter
from .converters.exceptions import ConvertError
from .converters.exceptions import MissingDependency
from .converters.exceptions import UnsupportedPlatform
from .util import ctx_params
from .util import get_avid
from .util import open_database


def handle_results(
    ctx: Context,
    database: FilesDB,
    src_table: Table,
    out_table: Table,
    instruction: ConvertInstructions[OriginalFile | MasterFile, ConvertedFile],
    output_files: list[ConvertedFile],
    error: ExceptionManager | None,
    set_processed: Callable[[OriginalFile | MasterFile], bool],
    commit_index: int,
    committer: Callable[[FilesDB, int], None],
) -> int:
    if error and isinstance(error.exception, ConvertError):
        event = Event.from_command(
            ctx,
            "error",
            instruction.file,
            {"tool": instruction.tool, "output": instruction.output, "converter": instruction.converter_cls.__name__},
            (error.exception.process.stderr or error.exception.process.stdout or None)
            if error.exception.process
            else "".join(format_tb(error.traceback)),
        )
        database.log.insert(event)
        return commit_index
    elif error and isinstance(error.exception, Exception):
        event = Event.from_command(
            ctx,
            "error",
            instruction.file,
            {"tool": instruction.tool, "output": instruction.output, "converter": instruction.converter_cls.__name__},
            "".join(format_tb(error.traceback)),
        )
        database.log.insert(event)
        return commit_index
    elif error and isinstance(error.exception, BaseException):
        raise error.exception

    commit_index += 1

    for output_file in output_files:
        out_table.insert(output_file)

    instruction.file.processed = set_processed(instruction.file)
    src_table.update(instruction.file)

    database.log.insert(
        Event.from_command(
            ctx,
            "converted",
            instruction.file,
            {
                "tool": instruction.tool,
                "output": instruction.output,
                "converter": instruction.converter_cls.__name__,
                "files": len(output_files),
            },
        )
    )

    committer(database, commit_index)

    return commit_index


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
    ),
)
@option("--tool-ignore", metavar="TOOL", type=str, multiple=True, help="Exclude specific tools.  [multiple]")
@option("--tool-include", metavar="TOOL", type=str, multiple=True, help="Include only specific tools.  [multiple]")
@option("--timeout", metavar="SECONDS", type=IntRange(min=0), default=None, help="Override converters' timeout.")
@option("--threads", type=IntRange(min=1), default=4, help="Set number of threads for async conversion.")
@option(
    "--commit",
    metavar="INTEGER",
    type=IntRange(0),
    default=1,
    show_default=True,
    help="Number of files edited per commit.",
)
@option("--dry-run", is_flag=True, default=False, help="Show changes without committing them.")
@option("--backup/--no-backup", is_flag=True, default=False, help="Create a backup of the database at start.")
@option("--verbose", is_flag=True, default=False, help="Show all outputs from converters.")
@pass_context
def cmd_digiarch(
    ctx: Context,
    avid_dir: str,
    target: str,
    query: tuple[str | None, list[str]],
    tool_ignore: tuple[str, ...],
    tool_include: tuple[str, ...],
    timeout: int | None,
    threads: int,
    commit: int,
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

    To restrict the tools that should be used for conversion, use the --tool-ignore and --tool-include options.
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
    output_dir: Path
    file_type: Literal["original", "master"]
    dest_type: Literal["master", "access", "statutory"]
    file_type, _, dest_type = target.partition(":")

    with open_database(ctx, avid, "avid_dir") as database:
        logger, _ = start_program(ctx, database, __version__, dry_run)

        if backup and not dry_run:
            backup_path: Path = avid.database_path.with_name(f"{datetime.now():%Y%m%d%H%M%S}-{avid.database_path.name}")
            Event.from_command(ctx, "backup:start").log(INFO, logger, name=backup_path.name)
            backup_path.unlink(missing_ok=True)
            copy2(avid.database_path, backup_path)
            Event.from_command(ctx, "backup:complete").log(INFO, logger, name=backup_path.name)

        src_table: Table[OriginalFile | MasterFile]
        out_table: Table[ConvertedFile]
        is_processed: Callable[[OriginalFile | MasterFile], bool]
        src_query: str
        set_processed: Callable[[OriginalFile | MasterFile], bool | int]
        committer: Callable[[FilesDB, int], None]

        if commit <= 0:
            committer = lambda _, __: None  # noqa: E731
        elif commit == 1:
            committer = lambda _db, _: _db.commit()  # noqa: E731
        else:
            committer = lambda _db, _n: _db.commit() if _n % commit == 0 else None  # noqa: E731

        with ExceptionManager(BaseException) as exception:
            if file_type == "original" and dest_type == "master":
                output_dir = avid.dirs.master_documents
                src_table = database.original_files
                out_table = database.master_files
                src_query = "action in ('convert', 'ignore')"
                is_processed = lambda f: f.processed  # noqa: E731
                set_processed = lambda _: True  # noqa: E731
            elif file_type == "master" and dest_type == "access":
                output_dir = avid.dirs.access_documents
                src_query = "convert_access is not null"
                src_table = database.master_files
                out_table = database.access_files
                is_processed = lambda f: f.processed & 0b01  # noqa: E731
                set_processed = lambda f: f.processed | 0b01  # noqa: E731
            elif file_type == "master" and dest_type == "statutory":
                output_dir = avid.dirs.documents
                src_query = "convert_statutory is not null"
                src_table = database.master_files
                out_table = database.statutory_files
                is_processed = lambda f: f.processed & 0b10  # noqa: E731
                set_processed = lambda f: f.processed | 0b10  # noqa: E731
            else:
                raise ValueError(f"Unsupported file and destination combination: {file_type}:{dest_type}")

            if query[0]:  # noqa: SIM108
                query = (f"({query[0]}) and ({src_query})", query[1])
            else:
                query = (src_query, [])

            Event.from_command(ctx, "compiling:start").log(INFO, logger)
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
                where {query[0] or "uuid is not null"}
                """,
                query[1],
            )
            database.commit()
            Event.from_command(ctx, "compiling:end").log(INFO, logger)

            output_dir.mkdir(parents=True, exist_ok=True)

            batch: tuple[OriginalFile | MasterFile, ...]
            commit_index: int = 0
            for batch in batched(
                (f for f in to_process_table.select(order_by=[("lower(relative_path)", "asc")]) if not is_processed(f)),
                threads * 2,
            ):
                instructions: list[
                    ConvertInstructions[
                        OriginalFile | MasterFile,
                        MasterFile | AccessFile | StatutoryFile,
                    ]
                ] = []

                for file in batch:
                    try:
                        if isinstance(file, OriginalFile):
                            instruction = original_file_converter(file)
                        else:
                            # noinspection PyTypeChecker
                            # dest_type cannot be anything but "access" or "statutory" when file is a MasterFile
                            instruction = master_file_converter(file, dest_type)
                        if instruction.tool in tool_ignore:
                            continue
                        if tool_include and instruction.tool not in tool_include:
                            continue
                        if timeout is not None:
                            instruction.converter_cls.process_timeout = None if timeout == 0 else float(timeout)
                        instructions.append(instruction)
                    except (ConvertError, UnsupportedPlatform, MissingDependency) as error:
                        Event.from_command(ctx, f"error:{error.__class__.__name__.lower()}", file).log(
                            ERROR,
                            logger,
                            tool=f"{file.action_data.convert.tool}:{file.action_data.convert.output}"
                            if file.action_data.convert
                            else None,
                            error=error.args[0],
                        )

                if dry_run:
                    for instruction in instructions:
                        Event.from_command(ctx, "convert", instruction.file).log(
                            INFO,
                            logger,
                            tool=[instruction.tool, instruction.output],
                        )
                    continue

                sync_queue, async_queues = file_queues(instructions, threads)

                for async_queue in async_queues:
                    for instruction, output_files, error in convert_async_queue(
                        ctx,
                        database,
                        output_dir,
                        async_queue,
                        threads,
                        verbose,
                        logger,
                    ):
                        handle_results(
                            ctx,
                            database,
                            src_table,
                            out_table,
                            instruction,
                            output_files,
                            error,
                            set_processed,
                            commit_index,
                            committer,
                        )

                for instruction, output_files, error in convert_queue(
                    ctx,
                    database,
                    output_dir,
                    sync_queue,
                    verbose,
                    logger,
                ):
                    handle_results(
                        ctx,
                        database,
                        src_table,
                        out_table,
                        instruction,
                        output_files,
                        error,
                        set_processed,
                        commit_index,
                        committer,
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
@option(
    "--option",
    "-o",
    "options",
    metavar="<KEY VALUE>",
    type=(str, str),
    multiple=True,
    help="Pass options to the converter.",
)
@option("--timeout", metavar="SECONDS", type=IntRange(min=0), default=None, help="Override converters' timeout.")
@option("--verbose", is_flag=True, default=False, help="Show all outputs from converters.")
@option(
    "--root",
    type=ClickPath(file_okay=False, writable=True, resolve_path=True),
    default=None,
    help="Set a root for the given files to keep the relative paths in the output.",
)
@pass_context
def cmd_standalone(
    ctx: Context,
    tool: str,
    output: str,
    destination: str,
    files_paths: tuple[str, ...],
    options: tuple[tuple[str, str], ...],
    timeout: int | None,
    verbose: bool,
    root: str | None,
):
    """
    Convert FILEs to OUTPUT with the given TOOL.

    The converted FILEs will be placed in the DESTINATION directory. To maintain the relative paths of the files, use
    the --root option to set their common parent directory.

    To pass options to the given converter tool, use the --option option with a KEY and VALUE. Values can only be
    strings.

    Use the --timeout option to override the converters' timeout, set to 0 to disable timeouts altogether.

    Use the --verbose option to print the standard output from the converters. The output (standard or error) is always
    printed in case of an error.
    """
    logger = structlog.stdlib.get_logger()

    if root and any(not Path(f).is_relative_to(root) for f in files_paths):
        raise BadParameter("not a parent path for all files.", ctx, ctx_params(ctx)["root"])

    dest: Path = Path(destination)
    dest.mkdir(parents=True, exist_ok=True)

    # noinspection PyTypeChecker
    try:
        # noinspection PyTypeChecker
        instructions = [
            original_file_converter(
                OriginalFile(
                    checksum="",
                    encoding=None,
                    relative_path=p.relative_to(root) if root else Path(p.name),
                    is_binary=False,
                    size=p.stat().st_size,
                    puid=None,
                    signature=None,
                    root=Path(root or p.parent),
                    action="convert",
                    action_data=ActionData(convert=ConvertAction(tool=tool, output=output, options=dict(options))),
                    original_path=p,
                )
            )
            for p_str in files_paths
            if (p := Path(p_str)).is_file()
        ]
    except (MissingDependency, UnsupportedPlatform) as error:
        logger.error(f"{error.__class__.__name__}: {' '.join(map(str, error.args))}")
        return
    except ConvertError as error:
        logger.error(f"{error.__class__.__name__}: {error.msg}")
        return

    for instruction in instructions:
        instruction.converter_cls.process_timeout = (
            timeout
            if timeout and instruction.converter_cls.process_timeout
            else instruction.converter_cls.process_timeout
        )
        converter = instruction.converter_cls(
            instruction.file,
            None,
            instruction.file.root,
            instruction.options,
            capture_output=not verbose,
        )
        # noinspection PyBroadException
        try:
            logger.info(f"<-- {instruction.file.relative_path}")
            for file in converter.convert(dest, instruction.output):
                logger.info(f"--> {file.relative_to(dest)}")
        except KeyboardInterrupt:
            raise
        except ConvertError as error:
            logger.error(error.msg)
        except BaseException as error:
            logger.exception(error.__class__.__name__)
