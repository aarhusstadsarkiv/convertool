from logging import ERROR
from logging import INFO
from logging import Logger
from pathlib import Path
from sqlite3 import DatabaseError
from typing import Type

from acacore.__version__ import __version__ as __acacore_version__
from acacore.database import FileDB
from acacore.database.upgrade import is_latest
from acacore.models.file import File
from acacore.models.history import HistoryEntry
from acacore.utils.click import end_program
from acacore.utils.click import start_program
from acacore.utils.helpers import ExceptionManager
from click import argument
from click import BadParameter
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
from .converters import ConverterCopy
from .converters import ConverterDocument
from .converters import ConverterImage
from .converters import ConverterMSG
from .converters import ConverterPDF
from .converters import ConverterPDFToImage
from .converters import ConverterPresentation
from .converters import ConverterSpreadsheet
from .converters import ConverterTemplate
from .converters import ConverterTextToImage
from .converters import ConverterTNEF
from .converters import ConverterVideo
from .converters.exceptions import ConvertError
from .util import ctx_params


def find_converter(tool: str, output: str) -> Type[ConverterABC] | None:
    for converter in (
        ConverterCopy,
        ConverterTemplate,
        ConverterTNEF,
        ConverterMSG,
        ConverterDocument,
        ConverterPresentation,
        ConverterSpreadsheet,
        ConverterPDFToImage,
        ConverterTextToImage,
        ConverterImage,
        ConverterAudio,
        ConverterVideo,
        ConverterPDF,
    ):
        if tool in converter.tool_names and output in converter.outputs:
            return converter

    return None


def root_callback(ctx: Context, param: Parameter, value: str):
    if not (path := Path(value)).joinpath("_metadata", "files.db").is_file():
        raise BadParameter(f"No _metadata/files.db present in {value!r}.", ctx, param)
    return path


def check_database_version(ctx: Context, param: Parameter, path: Path):
    if not path.is_file():
        return
    with FileDB(path, check_version=False) as db:
        try:
            is_latest(db, raise_on_difference=True)
        except DatabaseError as err:
            raise BadParameter(err.args[0], ctx, param)


def file_tool_output(file: File) -> tuple[str, str]:
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


def convert_file(
    ctx: Context,
    root: Path,
    database: FileDB,
    file: File,
    output_dir: Path,
    tool: str,
    output: str,
    *,
    verbose: bool = False,
    loggers: list[Logger] | None = None,
) -> list[Path]:
    loggers = loggers or []

    if tool in ConverterCopy.tool_names:
        output = ConverterCopy.outputs[0]

    converter_cls = find_converter(tool, output)

    if not converter_cls:
        raise ConvertError(file, f"No converter found for tool {tool!r} and output {output!r}")

    HistoryEntry.command_history(ctx, f"convert:{tool}.{output}", file.uuid).log(INFO, *loggers)
    converter: ConverterABC = converter_cls(file, database, root, capture_output=not verbose)
    dests: list[Path] = converter.convert(output_dir, output, keep_relative_path=True)
    for dst in dests:
        HistoryEntry.command_history(ctx, f"output:{tool}.{output}", file.uuid).log(INFO, *loggers, output=dst.name)
    return dests


@group("convertool", no_args_is_help=True)
@version_option(__version__, message=f"%(prog)s, version %(version)s\nacacore, version {__acacore_version__}")
def app(): ...


@app.command("digiarch", no_args_is_help=True)
@argument(
    "root",
    nargs=1,
    type=ClickPath(exists=True, file_okay=False, writable=True, resolve_path=True),
    callback=root_callback,
)
@argument(
    "output_dir",
    nargs=1,
    type=ClickPath(file_okay=False, writable=True, resolve_path=True),
    callback=lambda _c, _p, v: Path(v),
)
@option("--tool-ignore", metavar="TOOL", type=str, multiple=True, help="Exclude specific tools.  [multiple]")
@option("--tool-include", metavar="TOOL", type=str, multiple=True, help="Include only specific tools.  [multiple]")
@option("--dry-run", is_flag=True, default=False, help="Show changes without committing them.")
@option("--verbose", is_flag=True, default=False, help="Show all outputs from converters.")
@pass_context
def digiarch(
    ctx: Context,
    root: Path,
    output_dir: Path,
    tool_ignore: tuple[str, ...],
    tool_include: tuple[str, ...],
    dry_run: bool,
    verbose: bool,
):
    check_database_version(
        ctx,
        next(p for p in ctx.command.params if p.name == "root"),
        db_path := root.joinpath("_metadata", "files.db"),
    )

    with FileDB(db_path) as database:
        log_file, log_stdout, _ = start_program(ctx, database, __version__, None, not dry_run, True, False)

        with ExceptionManager(BaseException) as exception:
            offset: int = 0
            while files := list(
                database.files.select(
                    where="action in ('convert', 'ignore') and not processed",
                    limit=100,
                    offset=offset,
                )
            ):
                offset += len(files)

                for file in files:
                    tool, output = file_tool_output(file)

                    if tool_include and tool not in tool_include:
                        continue
                    if tool in tool_ignore:
                        continue

                    dests: list[Path] = []

                    try:
                        dests = convert_file(
                            ctx,
                            root,
                            database,
                            file,
                            output_dir,
                            tool,
                            output,
                            loggers=[log_stdout],
                            verbose=verbose,
                        )
                    except ConvertError as err:
                        HistoryEntry.command_history(ctx, "error", file.uuid, [tool, output], err.msg).log(
                            ERROR, log_stdout
                        )
                        for dst in dests:
                            dst.unlink(missing_ok=True)
                        continue
                    except BaseException:
                        for dst in dests:
                            dst.unlink(missing_ok=True)
                        raise

                    file.processed = True
                    database.files.update(file)
                    database.history.insert(HistoryEntry.command_history(ctx, "converted", file.uuid, [tool, output]))

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
@pass_context
def standalone(ctx: Context, tool: str, output: str, destination: str, files: tuple[str, ...]):
    converter_cls = find_converter(tool, output)

    if not converter_cls:
        raise BadParameter(f"cannot find converter for tool {tool} with output {output}", ctx, ctx_params(ctx)["tool"])

    dest: Path = Path(destination)

    for file_path in map(Path, files):
        file = File.from_file(file_path, file_path.parent)
        converter = converter_cls(file)
        try:
            converted_files = converter.convert(dest, output, keep_relative_path=False)
            for converted_file in converted_files:
                print(converted_file.relative_to(dest))
        except ConvertError as err:
            print(err.msg)
            raise Exit(1)
