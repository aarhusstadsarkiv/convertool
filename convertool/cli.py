from logging import ERROR
from logging import INFO
from logging import Logger
from logging import WARNING
from pathlib import Path
from sqlite3 import DatabaseError
from typing import Callable
from typing import Literal
from typing import Type

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
from click import option
from click import Parameter
from click import pass_context
from click import Path as ClickPath
from click import version_option
from click.exceptions import Exit

from .__version__ import __version__
from .converters import ConverterABC
from .converters import ConverterAudio
from .converters import ConverterCAD
from .converters import ConverterCopy
from .converters import ConverterDocument
from .converters import ConverterDocumentToImage
from .converters import ConverterGIS
from .converters import ConverterHTML
from .converters import ConverterHTMLToImage
from .converters import ConverterImage
from .converters import ConverterMSG
from .converters import ConverterMSGToImage
from .converters import ConverterMSGToPDF
from .converters import ConverterPDF
from .converters import ConverterPDFToImage
from .converters import ConverterPresentation
from .converters import ConverterSpreadsheet
from .converters import ConverterSymphovert
from .converters import ConverterTemplate
from .converters import ConverterTextToImage
from .converters import ConverterTNEF
from .converters import ConverterVideo
from .converters.exceptions import ConvertError
from .converters.exceptions import MissingDependency
from .converters.exceptions import UnsupportedPlatform
from .util import AVID
from .util import ctx_params
from .util import get_avid
from .util import open_database


def find_converter(tool: str, output: str) -> Type[ConverterABC] | None:
    for converter in (
        ConverterCopy,
        ConverterTemplate,
        ConverterSymphovert,
        ConverterGIS,
        ConverterHTML,
        ConverterHTMLToImage,
        ConverterCAD,
        ConverterTNEF,
        ConverterMSG,
        ConverterMSGToImage,
        ConverterMSGToPDF,
        ConverterDocument,
        ConverterDocumentToImage,
        ConverterPresentation,
        ConverterSpreadsheet,
        ConverterPDFToImage,
        ConverterTextToImage,
        ConverterImage,
        ConverterAudio,
        ConverterVideo,
        ConverterPDF,
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


def original_file_tool_output(file: OriginalFile) -> tuple[str, str]:
    if file.action == "convert" and not file.action_data.convert:
        raise ValueError("Missing convert action data", file)
    elif file.action == "convert":
        return file.action_data.convert.tool, file.action_data.convert.output
    elif file.action == "ignore" and not file.action_data.ignore:
        raise ValueError("Missing ignore action data", file)
    elif file.action == "ignore":
        return "template", file.action_data.ignore.template
    else:
        raise ValueError(f"Unsupported action {file.action!r}", file)


def master_file_tool_output(file: MasterFile, dest_type: Literal["access", "statutory"]) -> tuple[str, str]:
    if dest_type == "access" and not file.convert_access:
        raise ValueError("Missing convert action data", file)
    elif dest_type == "access":
        return file.convert_access.tool, file.convert_access.output
    elif dest_type == "statutory" and not file.convert_statutory:
        raise ValueError("Missing convert action data", file)
    elif dest_type == "statutory":
        return file.convert_statutory.tool, file.convert_statutory.output
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
    *,
    verbose: bool = False,
    loggers: list[Logger] | None = None,
    dry_run: bool = False,
) -> list[ConvertedFile]:
    loggers = loggers or []
    root_dir: Path
    output_dir: Path
    dst_cls: Type[ConvertedFile]
    dst_table: Table[ConvertedFile]

    if tool in ConverterCopy.tool_names:
        output = ConverterCopy.outputs[0]

    converter_cls = find_converter(tool, output)

    if not converter_cls:
        raise ConvertError(file, f"No converter found for tool {tool!r} and output {output!r}")

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
    converter: ConverterABC = converter_cls(file_copy, database, avid.path, capture_output=not verbose)
    dest_paths: list[Path] = converter.convert(output_dir, output, keep_relative_path=True)
    dest_files: list[ConvertedFile] = []

    for dst in dest_paths:
        dst_file = dst_cls.from_file(dst, avid.path, file.uuid)
        dst_table.insert(dst_file, on_exists="replace")
        Event.from_command(ctx, f"out:{tool}.{output}", (file.uuid, dest_type)).log(INFO, *loggers, output=dst.name)
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
@option("--dry-run", is_flag=True, default=False, help="Show changes without committing them.")
@option("--verbose", is_flag=True, default=False, help="Show all outputs from converters.")
@pass_context
def digiarch(
    ctx: Context,
    avid_dir: str,
    target: str,
    tool_ignore: tuple[str, ...],
    tool_include: tuple[str, ...],
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
                        tool, output = original_file_tool_output(file)
                    elif file_type == "master":
                        # noinspection PyTypeChecker
                        tool, output = master_file_tool_output(file, dest_type)

                    if tool_include and tool not in tool_include:
                        continue
                    if tool in tool_ignore:
                        continue

                    try:
                        output_files: list[ConvertedFile] = convert_file(
                            ctx,
                            avid,
                            database,
                            file,
                            file_type,
                            dest_type,
                            tool,
                            output,
                            loggers=[log_stdout],
                            verbose=verbose,
                            dry_run=dry_run,
                        )
                    except (MissingDependency, UnsupportedPlatform) as err:
                        Event.from_command(ctx, "warning", (file.uuid, file_type)).log(
                            WARNING,
                            log_stdout,
                            error=repr(err),
                        )
                        continue
                    except ConvertError as err:
                        Event.from_command(ctx, "error", (file.uuid, file_type)).log(
                            ERROR,
                            log_stdout,
                            tool=[tool, output],
                            error=err.msg,
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
@option("--verbose", is_flag=True, default=False, help="Show all outputs from converters.")
@pass_context
def standalone(ctx: Context, tool: str, output: str, destination: str, files: tuple[str, ...], verbose: bool):
    converter_cls = find_converter(tool, output)

    if not converter_cls:
        raise BadParameter(f"cannot find converter for tool {tool} with output {output}", ctx, ctx_params(ctx)["tool"])

    dest: Path = Path(destination)
    dest.mkdir(parents=True, exist_ok=True)

    for file_path in map(Path, files):
        try:
            file = BaseFile.from_file(file_path, file_path.parent)
            converter = converter_cls(file, capture_output=not verbose)
            converted_files = converter.convert(dest, output, keep_relative_path=False)
            for converted_file in converted_files:
                print(converted_file.relative_to(dest))
        except (MissingDependency, UnsupportedPlatform) as err:
            print(repr(err))
            raise Exit(1)
        except ConvertError as err:
            print(err.msg)
            raise Exit(1)
