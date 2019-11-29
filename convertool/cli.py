"""Convertool enables conversion of several file types to pdf.

"""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import platform
import math
from typing import List
import click
from click.core import Context as ClickContext
from convertool.convert import convert_files
from convertool.utils import get_files, check_system, ACCEPTED_OUT
from convertool.exceptions import WrongOSError, ConversionError

# -----------------------------------------------------------------------------
# Function Definitions
# -----------------------------------------------------------------------------


@click.group()
@click.argument(
    "files", type=click.Path(exists=True, file_okay=True, resolve_path=True)
)
@click.argument(
    "outdir", type=click.Path(exists=True, file_okay=False, resolve_path=True)
)
@click.option(
    "--parents",
    default=0,
    show_default=True,
    help="Number of parent directories to use for output name.",
)
@click.option(
    "--to",
    "to_",
    type=click.Choice(ACCEPTED_OUT, case_sensitive=False),
    default="pdf",
    help="File format to convert to. Defaults to PDF.",
)
@click.pass_context
def cli(
    ctx: ClickContext, files: str, outdir: str, parents: int, to_: str
) -> None:
    """Convert files from a folder or a list. If FILES is a folder,
    convertool will convert every file in this folder and subfolders.
    If FILES is a file, convertool expects a text file with a list of
    files to convert. OUTDIR specifies the directory in which to output
    converted files. It must be an existing directory."""
    try:
        check_system(platform.system())
    except WrongOSError as error:
        raise click.ClickException(str(error))
    else:
        file_list: List[str] = get_files(files)
        if not file_list:
            raise click.ClickException(f"{files} is empty. Aborting.")

        # Create object with state to pass around.
        ctx.obj = {
            "file_list": file_list,
            "outdir": outdir,
            "convert_to": to_,
            "parents": parents,
            "max_errs": int(math.sqrt(len(file_list))),
        }


@cli.command()
@click.pass_obj
def libre(ctx: dict) -> None:
    """Convert files using LibreOffice."""
    try:
        convert_files(
            "libre",
            ctx["file_list"],
            ctx["outdir"],
            ctx["convert_to"],
            ctx["parents"],
            ctx["max_errs"],
        )
    except ConversionError as error:
        raise click.ClickException(str(error))
