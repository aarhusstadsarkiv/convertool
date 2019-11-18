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

# -----------------------------------------------------------------------------
# Function Definitions
# -----------------------------------------------------------------------------


@click.group()
@click.argument(
    "files", type=click.Path(exists=True, file_okay=True, resolve_path=True)
)
@click.pass_context
def cli(ctx: click.core.Context, files: str) -> None:
    """Convert files from a folder or a list. If FILES is a folder,
    convertool will convert every file in this folder and subfolders.
    If FILES is a file, convertool expects a text file with a list of
    files to convert."""
    system: str = platform.system()
    if system in ["Windows", "Linux"]:
        file_list: List[str] = get_files(files)
        if not file_list:
            exit_msg = f"{files} is empty. Aborting."
            raise click.ClickException(exit_msg)
        ctx.obj = {"file_list": file_list, "system": system}
    else:
        exit_msg = f"Expected to run on Windows or Linux, got {system}."
        raise click.ClickException(exit_msg)


@cli.command()
@click.pass_obj
def msoffice(context: dict) -> None:
    """Generate reports on files and directory structure."""
    ms_convert(context["system"], context["file_list"])


if __name__ == "__main__":
    sys.exit(cli())  # noqa
