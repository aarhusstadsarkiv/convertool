"""Convertool enables conversion of several file types to pdf.

"""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import platform
from typing import List
import click
from convertool.libreoffice import convert_files as libre_convert
from convertool.utils import get_files
from convertool.utils import check_system, WrongOSError

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
SYSTEM = platform.system()

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
@click.pass_context
def cli(ctx: click.core.Context, files: str, outdir: str) -> None:
    """Convert files from a folder or a list. If FILES is a folder,
    convertool will convert every file in this folder and subfolders.
    If FILES is a file, convertool expects a text file with a list of
    files to convert. OUTDIR specifies the directory in which to output
    converted files. It must be an existing directory."""
    try:
        check_system(SYSTEM)
    except WrongOSError as error:
        raise click.ClickException(str(error))
    else:
        file_list: List[str] = get_files(files)
        if not file_list:
            exit_msg = f"{files} is empty. Aborting."
            raise click.ClickException(exit_msg)

        # Create object with state to pass around.
        ctx.obj = {"file_list": file_list, "outdir": outdir}


@cli.command()
@click.pass_obj
def libre(context: dict) -> None:
    """Convert files using LibreOffice."""
    try:
        libre_convert(context["file_list"], context["outdir"])
    except Exception as error:
        raise click.ClickException(str(error))
