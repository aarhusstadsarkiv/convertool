from pathlib import Path
from typing import Type

from acacore.__version__ import __version__ as __acacore_version__
from acacore.models.file import File
from click import argument
from click import BadParameter
from click import Context
from click import group
from click import pass_context
from click import Path as ClickPath
from click import version_option
from click.exceptions import Exit

from .__version__ import __version__
from .converters.base import Converter
from .converters.converter_to_img import ConverterPDFToImg
from .converters.converter_to_img import ConverterTextToImg
from .converters.converter_to_img import ConverterToImg
from .converters.converter_to_pdf import ConverterToPdf
from .converters.converter_to_video import ConverterToVideo
from .converters.exceptions import ConvertError
from .util import ctx_params


def find_converter(tool: str, output: str) -> Type[Converter] | None:
    for converter in (
        ConverterPDFToImg,
        ConverterTextToImg,
        ConverterToImg,
        ConverterToVideo,
        ConverterToPdf,
    ):
        if tool in converter.tool_names and output in converter.outputs:
            return converter


@group("convertool", no_args_is_help=True)
@version_option(__version__, message=f"%(prog)s, version %(version)s\nacacore, version {__acacore_version__}")
def app(): ...


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
