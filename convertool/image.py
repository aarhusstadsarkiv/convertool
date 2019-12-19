"""Tool for reading and converting image files.

"""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
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
    save_all: bool = False
    outfile: Path = outdir.joinpath(f"{file.stem}.{convert_to}")
    if convert_to.lower() == "pdf":
        save_all = True
    try:
        Image.open(file).save(outfile, save_all=save_all)
    except IOError as error:
        raise ImageError(error)
