"""Convertool enables conversion of several file types to pdf.

"""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import sys
import platform
from typing import List
import click

# Note: mypy doesn't like . imports, so we pass a type: ignore[import] comment.
# pylint doesn't like this either. :)
# pylint: disable=locally-disabled, relative-beyond-top-level
from .msoffice import convert_files as ms_convert  # type: ignore[import]
from .utils import get_files  # type: ignore[import]
from .utils import check_system, WrongOSError  # type: ignore[import]

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
    files to convert."""
    system: str = platform.system()
    try:
        check_system(system)
    except WrongOSError as error:
        raise click.ClickException(error)
    else:
        file_list: List[str] = get_files(files)
        if not file_list:
            exit_msg = f"{files} is empty. Aborting."
            raise click.ClickException(exit_msg)

        # Create object with state to pass around.
        ctx.obj = {"file_list": file_list, "system": system, "outdir": outdir}


@cli.command()
@click.pass_obj
def msoffice(context: dict) -> None:
    """Generate reports on files and directory structure."""
    ms_convert(context["system"], context["file_list"], context["outdir"])


if __name__ == "__main__":
    sys.exit(cli())  # noqa
