"""Tool for reading and converting image files.

"""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import subprocess
from pathlib import Path

from PIL import Image

from .exceptions import ImageError

# -----------------------------------------------------------------------------
# Function Definitions
# -----------------------------------------------------------------------------


def image_convert(file: Path, outdir: Path, convert_to: str) -> None:
    """Description

    Parameters
    ----------
    param : type
        desc

    Returns
    -------
    return : type
        desc

    Raises
    ------
    BadError

    """
    outfile: Path = outdir.joinpath(f"{file.stem}.{convert_to}")
    if (
        file.suffix.lower() in [".tif", ".tiff"]
        and convert_to.lower() == "pdf"
    ):
        try:
            subprocess.run(
                f'tiff2pdf -d "{file}" -o "{outfile}"',
                shell=True,
                capture_output=True,
                check=True,
            )
        except Exception as error:
            raise ImageError(error)
    else:
        try:
            Image.open(file).save(outfile)
        except Exception as error:
            raise ImageError(error)
