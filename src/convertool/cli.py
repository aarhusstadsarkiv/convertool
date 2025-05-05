from collections.abc import Callable
from logging import ERROR
from logging import INFO
from logging import Logger
from logging import WARNING
from pathlib import Path
from sqlite3 import DatabaseError
from traceback import format_tb
from typing import Any
from typing import Literal

from acacore.__version__ import __version__ as __acacore_version__
from acacore.database import FilesDB
from acacore.database.table import Table
from acacore.database.upgrade import is_latest
from acacore.models.event import Event
from acacore.models.file import BaseFile
from acacore.models.file import ConvertedFile
from acacore.models.file import MasterFile
from acacore.models.file import OriginalFile
from acacore.utils.click import end_program
from acacore.utils.click import start_program
from acacore.utils.helpers import ExceptionManager
from click import argument
from click import BadParameter
from click import Choice
from click import Context
from click import group
from click import IntRange
from click import option
from click import Parameter
from click import pass_context
from click import Path as ClickPath
from click import version_option
from click.exceptions import Exit

from . import converters
from .__version__ import __version__
from .converters.exceptions import ConvertError
from .converters.exceptions import MissingDependency
from .converters.exceptions import UnsupportedPlatform
from .util import AVID
from .util import ctx_params
from .util import get_avid
from .util import open_database


def find_converter(tool: str, output: str) -> type[converters.ConverterABC] | None:
    for converter in (
        converters.ConverterCopy,
        converters.ConverterTemplate,
        converters.ConverterSymphovert,
        converters.ConverterGIS,
        converters.ConverterHTML,
        converters.ConverterHTMLToImage,
        converters.ConverterCAD,
        converters.ConverterTNEF,
        converters.ConverterMedCom,
        converters.ConverterMedComToImage,
        converters.ConverterMedComToPDF,
        converters.ConverterMSG,
        converters.ConverterMSGToImage,
        converters.ConverterMSGToPDF,
        converters.ConverterMSExcel,
        converters.ConverterMSPowerPoint,
        converters.ConverterMSWord,
        converters.ConverterDocument,
        converters.ConverterDocumentToImage,
        converters.ConverterPresentation,
        converters.ConverterSpreadsheet,
        converters.ConverterSAS,
        converters.ConverterPDFToImage,
        converters.ConverterPDFLargeToImage,
        converters.ConverterTextToImage,
        converters.ConverterImage,
        converters.ConverterAudio,
        converters.ConverterVideo,
        converters.ConverterPDF,
        converters.ConverterXSL,
        converters.ConverterXSLToImage,
        converters.ConverterXSLToPDF,
        converters.ConverterZIPFile,
    ):
        if converter.match_tool(tool, output):
            return converter

    return None


def root_callback(ctx: Context, param: Parameter, value: str):
    if not (path := Path(value)).joinpath("_metadata", "files.db").is_file():
        raise BadParameter(f"No _metadata/files.db present in {value!r}.", ctx, param)
    return path


def check_database_version(ctx: Context, param: Parameter, path: Path):
    if not path.is_file():
        return
    with FilesDB(path, check_version=False) as db:
        try:
            is_latest(db.connection, raise_on_difference=True)
        except DatabaseError as err:
            raise BadParameter(err.args[0], ctx, param)


def original_file_tool_output(file: OriginalFile) -> tuple[str, str, dict[str, Any] | None]:
    if file.action == "convert" and not file.action_data.convert:
        raise ValueError("Missing convert action data", file)
    if file.action == "convert":
        return file.action_data.convert.tool, file.action_data.convert.output, file.action_data.convert.options
    elif file.action == "ignore" and not file.action_data.ignore:
        raise ValueError("Missing ignore action data", file)
    elif file.action == "ignore":
        return "template", file.action_data.ignore.template, None
    else:
        raise ValueError(f"Unsupported action {file.action!r}", file)


def master_file_tool_output(
    file: MasterFile,
    dest_type: Literal["access", "statutory"],
) -> tuple[str, str, dict[str, Any] | None]:
    if dest_type == "access" and not file.convert_access:
        raise ValueError("Missing convert action data", file)
    if dest_type == "access":
        return file.convert_access.tool, file.convert_access.output, file.convert_access.options
    elif dest_type == "statutory" and not file.convert_statutory:
        raise ValueError("Missing convert action data", file)
    elif dest_type == "statutory":
        return file.convert_statutory.tool, file.convert_statutory.output, file.convert_statutory.options
    else:
        raise ValueError(f"Unsupported action {file.action!r}", file)


def convert_file(
    ctx: Context,
    avid: AVID,
    database: FilesDB,
    file: BaseFile,
    file_type: Literal["original", "master"],
    dest_type: Literal["master", "access", "statutory"],
    tool: str,
    output: str,
    options: dict[str, Any] | None,
    *,
    verbose: bool = False,
    loggers: list[Logger] | None = None,
    dry_run: bool = False,
    timeout: int | None = None,
) -> list[ConvertedFile]:
    loggers = loggers or []
    root_dir: Path
    output_dir: Path
    dst_cls: type[ConvertedFile]
    dst_table: Table[ConvertedFile]

    if tool in converters.ConverterCopy.tool_names:
        output = converters.ConverterCopy.outputs[0]

    converter_cls = find_converter(tool, output)

    if not converter_cls:
        raise ConvertError(file, f"No converter found for tool {tool!r} and output {output!r}")

    if timeout is not None:
        converter_cls.process_timeout = None if timeout == 0 else float(timeout)

    if file_type == "original":
        root_dir = avid.dirs.original_documents
    elif file_type == "master":
        root_dir = avid.dirs.master_documents
    else:
        raise ValueError(f"Unknown source file type {file_type!r}")

    if dest_type == "master":
        output_dir = avid.dirs.master_documents
        dst_cls = MasterFile
        dst_table = database.master_files
    elif dest_type == "access":
        output_dir = avid.dirs.access_documents
        dst_cls = ConvertedFile
        dst_table = database.access_files
    elif dest_type == "statutory":
        output_dir = avid.dirs.documents
        dst_cls = ConvertedFile
        dst_table = database.statutory_files
    else:
        raise ValueError(f"Unknown destination file type {dest_type!r}")

    Event.from_command(ctx, f"run:{tool}.{output}", (file.uuid, file_type)).log(INFO, *loggers)

    if dry_run:
        return []

    output_dir.mkdir(parents=True, exist_ok=True)

    file_copy = file.model_copy(deep=True)
    file_copy.relative_path = file.get_absolute_path(avid.path).relative_to(root_dir)
    file_copy.root = root_dir
    converter: converters.ConverterABC = converter_cls(
        file_copy,
        database,
        avid.path,
        options,
        capture_output=not verbose,
    )
    dest_paths: list[Path] = converter.convert(output_dir, output, keep_relative_path=True)
    dest_files: list[ConvertedFile] = []

    for dst in dest_paths:
        dst_file = dst_cls.from_file(dst, avid.path, file.uuid)
        dst_file.puid = converter.output_puid(output)
        dst_table.insert(dst_file, on_exists="replace")
        Event.from_command(ctx, f"out:{tool}.{output}", (dst_file.uuid, dest_type)).log(INFO, *loggers, output=dst.name)
        dest_files.append(dst_file)

    return dest_files


@group("convertool", no_args_is_help=True)
@version_option(__version__, message=f"%(prog)s, version %(version)s\nacacore, version {__acacore_version__}")
def app(): ...


@app.command("digiarch", no_args_is_help=True)
@argument(
    "avid_dir",
    type=ClickPath(exists=True, file_okay=False, writable=True, resolve_path=True),
    required=True,
)
@argument("target", type=Choice(["original:master", "master:access", "master:statutory"]), required=True)
@option("--tool-ignore", metavar="TOOL", type=str, multiple=True, help="Exclude specific tools.  [multiple]")
@option("--tool-include", metavar="TOOL", type=str, multiple=True, help="Include only specific tools.  [multiple]")
@option("--timeout", metavar="SECONDS", type=IntRange(min=0), default=None, help="Override converters' timeout.")
@option("--dry-run", is_flag=True, default=False, help="Show changes without committing them.")
@option("--verbose", is_flag=True, default=False, help="Show all outputs from converters.")
@pass_context
def digiarch(
    ctx: Context,
    avid_dir: str,
    target: str,
    tool_ignore: tuple[str, ...],
    tool_include: tuple[str, ...],
    timeout: int | None,
    dry_run: bool,
    verbose: bool,
):
    avid = get_avid(ctx, avid_dir, "avid_dir")
    file_type: Literal["original", "master"]
    dest_type: Literal["master", "access", "statutory"]
    file_type, _, dest_type = target.partition(":")

    with open_database(ctx, avid, "avid_dir") as database:
        log_file, log_stdout, _ = start_program(ctx, database, __version__, None, not dry_run, True, False)

        src_table: Table[OriginalFile | MasterFile]
        query: str
        is_processed: Callable[[OriginalFile | MasterFile], bool]
        set_processed: Callable[[OriginalFile | MasterFile], bool | int]

        if file_type == "original":
            src_table = database.original_files
            query = "action in ('convert', 'ignore')"
            is_processed = lambda f: f.processed  # noqa: E731
            set_processed = lambda _: True  # noqa: E731
        elif file_type == "master" and dest_type == "access":
            query = "convert_access is not null"
            src_table = database.master_files
            is_processed = lambda f: f.processed & 0b01  # noqa: E731
            set_processed = lambda f: f.processed | 0b01  # noqa: E731
        elif file_type == "master" and dest_type == "statutory":
            query = "convert_statutory is not null"
            src_table = database.master_files
            is_processed = lambda f: f.processed & 0b10  # noqa: E731
            set_processed = lambda f: f.processed | 0b10  # noqa: E731

        with ExceptionManager(BaseException) as exception:
            offset: int = 0
            while files := src_table.select(
                query,
                order_by=[("lower(relative_path)", "asc")],
                limit=100,
                offset=offset,
            ).fetchall():
                offset += len(files)

                for file in files:
                    if is_processed(file):
                        continue

                    if file_type == "original":
                        tool, output, options = original_file_tool_output(file)
                    elif file_type == "master":
                        # noinspection PyTypeChecker
                        tool, output, options = master_file_tool_output(file, dest_type)

                    if tool_include and tool not in tool_include:
                        continue
                    if tool in tool_ignore:
                        continue

                    with ExceptionManager(MissingDependency, UnsupportedPlatform, ConvertError) as convert_error:
                        output_files: list[ConvertedFile] = convert_file(
                            ctx,
                            avid,
                            database,
                            file,
                            file_type,
                            dest_type,
                            tool,
                            output,
                            options,
                            loggers=[log_stdout],
                            verbose=verbose,
                            dry_run=dry_run,
                            timeout=timeout,
                        )

                    if isinstance(convert_error.exception, MissingDependency | UnsupportedPlatform):
                        Event.from_command(ctx, "warning", (file.uuid, file_type)).log(
                            WARNING,
                            log_stdout,
                            error=repr(convert_error.exception),
                        )
                        continue
                    if isinstance(convert_error.exception, ConvertError):
                        error = Event.from_command(
                            ctx,
                            "error",
                            (file.uuid, file_type),
                            {"tool": tool, "output": output},
                            (convert_error.exception.process.stderr or convert_error.exception.process.stdout or None)
                            if convert_error.exception.process
                            else "".join(format_tb(convert_error.traceback)),
                        )
                        database.log.insert(error)
                        error.log(
                            ERROR,
                            log_stdout,
                            show_args=["uuid"],
                            tool=[tool, output],
                            error=convert_error.exception.msg,
                        )
                        continue
                    if convert_error.exception:
                        error = Event.from_command(
                            ctx,
                            "error",
                            (file.uuid, file_type),
                            {"tool": tool, "output": output},
                            "".join(format_tb(convert_error.traceback)),
                        )
                        database.log.insert(error)
                        error.log(
                            ERROR,
                            log_stdout,
                            show_args=["uuid"],
                            tool=[tool, output],
                            error=repr(convert_error.exception),
                        )
                        continue

                    if dry_run:
                        continue

                    file.processed = set_processed(file)
                    src_table.update(file)
                    database.log.insert(
                        Event.from_command(
                            ctx,
                            "converted",
                            (file.uuid, file_type),
                            {"tool": tool, "output": output, "files": len(output_files)},
                        )
                    )

        end_program(ctx, database, exception, dry_run, log_file, log_stdout)


@app.command("standalone", no_args_is_help=True)
@argument("tool", nargs=1)
@argument("output", nargs=1)
@argument("destination", nargs=1, type=ClickPath(file_okay=False, writable=True, resolve_path=True))
@argument(
    "files",
    metavar="FILE...",
    nargs=-1,
    type=ClickPath(exists=True, dir_okay=False, readable=True, resolve_path=True),
    required=True,
)
@option("--option", "-o", "options", type=(str, str), multiple=True, help="Pass options to the converter.")
@option("--timeout", metavar="SECONDS", type=IntRange(min=0), default=None, help="Override converters' timeout.")
@option("--verbose", is_flag=True, default=False, help="Show all outputs from converters.")
@option(
    "--root",
    type=ClickPath(file_okay=False, writable=True, resolve_path=True),
    default=None,
    help="Set a root for the given files to keep the relative paths in the output.",
)
@pass_context
def standalone(
    ctx: Context,
    tool: str,
    output: str,
    destination: str,
    files: tuple[str, ...],
    options: tuple[tuple[str, str], ...],
    timeout: int | None,
    verbose: bool,
    root: str | None,
):
    if root and any(not Path(f).is_relative_to(root) for f in files):
        raise BadParameter("not a parent path for all files.", ctx, ctx_params(ctx)["root"])

    converter_cls = find_converter(tool, output)

    if not converter_cls:
        raise BadParameter(f"cannot find converter for tool {tool} with output {output}.", ctx, ctx_params(ctx)["tool"])

    if timeout is not None:
        converter_cls.process_timeout = None if timeout == 0 else float(timeout)

    dest: Path = Path(destination)
    dest.mkdir(parents=True, exist_ok=True)

    for file_path in map(Path, files):
        try:
            file = BaseFile.from_file(file_path, root or file_path.parent)
            converter = converter_cls(file, options=dict(options), capture_output=not verbose)
            converted_files = converter.convert(dest, output, keep_relative_path=root is not None)
            for converted_file in converted_files:
                print(converted_file.relative_to(dest))
        except (MissingDependency, UnsupportedPlatform) as err:
            print(repr(err))
            raise Exit(1)
        except ConvertError as err:
            print(err.msg)
            raise Exit(1)
