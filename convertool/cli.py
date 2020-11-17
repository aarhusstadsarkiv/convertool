"""Convertool enables conversion of several file types to pdf.

"""
# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import asyncio
from functools import wraps
from typing import Any
from typing import Callable
from typing import List
from typing import Optional

import click
from acamodels import ArchiveFile
from click.core import Context as ClickContext

from convertool import core
from convertool.database import FileDB
from convertool.exceptions import ConversionError

# -----------------------------------------------------------------------------
# Auxiliary functions
# -----------------------------------------------------------------------------


def coro(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return asyncio.run(func(*args, **kwargs))

    return wrapper


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------


@click.group()
@click.argument(
    "files", type=click.Path(exists=True, file_okay=True, resolve_path=True)
)
@click.argument(
    "outdir", type=click.Path(exists=True, file_okay=False, resolve_path=True)
)
@click.option(
    "--threshold",
    "max_errs",
    type=int,
    default=None,
    help="How many errors the conversion process should accept. "
    "If None (default), it will be calculated as sqrt(#files) and "
    "rounded to the nearest integer.",
)
@click.pass_context
@coro
async def cli(
    ctx: ClickContext,
    files: str,
    outdir: str,
    max_errs: Optional[int],
) -> None:
    """Convert files from a digiarch generated file database.
    OUTDIR specifies the directory in which to output converted files.
    It must be an existing directory."""

    try:
        file_db: FileDB = FileDB(f"sqlite:///{files}")
    except Exception:
        raise click.ClickException(f"Failed to load {files} as a database.")
    else:
        files_: List[ArchiveFile] = await file_db.get_files()
        if not files_:
            raise click.ClickException("Database is empty. Aborting.")

    ctx.obj = core.FileConv(
        files=files_,
        out_dir=outdir,
        max_errs=max_errs,
    )


@cli.command()
@click.pass_obj
def libre(file_conv: core.FileConv) -> None:
    """Convert files using LibreOffice."""
    try:
        file_conv.convert()
    except ConversionError as error:
        raise click.ClickException(str(error))


# @cli.command()
# @click.pass_obj
# def context(file_conv: core.FileConv) -> None:
#     """Convert context documentation files from PDF to TIFF."""
#     try:
#         core.convert_files("context", file_conv)
#     except ConversionError as error:
#         raise click.ClickException(str(error))
