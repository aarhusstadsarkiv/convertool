from logging import INFO
from pathlib import Path
from shutil import copy2
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
from .converters.base import Converter
from .converters.converter_to_img import ConverterPDFToImg
from .converters.converter_to_img import ConverterTextToImg
from .converters.converter_to_img import ConverterToImg
from .converters.converter_to_pdf import ConverterToPDF
from .converters.converter_to_video import ConverterToVideo
from .converters.exceptions import ConvertError
from .util import ctx_params


def find_converter(tool: str, output: str) -> Type[Converter] | None:
    for converter in (
        ConverterPDFToImg,
        ConverterTextToImg,
        ConverterToImg,
        ConverterToVideo,
        ConverterToPDF,
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


def convert_file(
    ctx: Context,
    root: Path,
    database: FileDB,
    file: File,
    output_dir: Path,
) -> tuple[list[Path], list[HistoryEntry]]:
    if not file.action_data.convert:
        return [], [HistoryEntry.command_history(ctx, "error", file.uuid, None, "Missing convert action data")]

    tool, outputs = file.action_data.convert.tool, file.action_data.convert.outputs
    dests: list[Path] = []

    if tool == "copy":
        dst = output_dir.joinpath(file.relative_path)
        dst.parent.mkdir(parents=True, exist_ok=True)
        copy2(file.get_absolute_path(root), dst)
        return [dst], [HistoryEntry.command_history(ctx, "copy", file.uuid, dst)]

    for output in outputs:
        if not (converter_cls := find_converter(tool, output)):
            return [], [
                HistoryEntry.command_history(
                    ctx,
                    "error",
                    file.uuid,
                    None,
                    f"Converter not found for tool {tool} output {output}",
                )
            ]
        converter: Converter = converter_cls(file, database, root)
        dests.extend(converter.convert(output_dir, output, keep_relative_path=True))

    return dests, [HistoryEntry.command_history(ctx, "convert", file.uuid, dst) for dst in dests]


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
@pass_context
def digiarch(
    ctx: Context,
    root: Path,
    output_dir: Path,
    tool_ignore: tuple[str, ...],
    tool_include: tuple[str, ...],
    dry_run: bool,
):
    check_database_version(
        ctx,
        next(p for p in ctx.command.params if p.name == "root"),
        db_path := root.joinpath("_metadata", "files.db"),
    )

    with FileDB(db_path) as database:
        log_file, log_stdout, _ = start_program(ctx, database, __version__, None, not dry_run, True, False)

        with ExceptionManager(BaseException) as exception:
            while files := list(database.files.select(where="action = 'convert' and not processed", limit=100)):
                for file in files:
                    if tool_include and file.action_data.convert.tool not in tool_include:
                        continue
                    if file.action_data.convert.tool in tool_ignore:
                        continue
                    dests, history = convert_file(ctx, root, database, file, output_dir)
                    file.processed = True
                    database.files.update(file)
                    for dst, event in zip(dests, history):
                        event.log(INFO, log_stdout)
                        database.history.insert(event)

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
