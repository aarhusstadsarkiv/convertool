"""Convertool internals.

"""
# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import math
from pathlib import Path
from typing import Any, List, Optional, Dict

from pydantic import BaseModel, validator, root_validator


# -----------------------------------------------------------------------------
# Globals
# -----------------------------------------------------------------------------
ACCEPTED_OUT = ["pdf", "ods", "odt", "odp", "html", "png", "tiff"]

# -----------------------------------------------------------------------------
# Data Models
# -----------------------------------------------------------------------------


class Identification(BaseModel):
    """File identification information model."""

    puid: Optional[str]
    signame: Optional[str]
    warning: Optional[str]


class FileInfo(BaseModel):
    """File information model."""

    path: Path
    name: str = ""
    ext: str = ""
    size: str = ""
    checksum: Optional[str]
    identification: Optional[Identification]

    @validator("path")
    def path_must_be_file(cls, path: Path) -> Path:
        if not path.is_file():
            raise ValueError("File does not exist.")
        return path.resolve()

    @root_validator
    def overwrite(cls, values: Dict[Any, Any]) -> Dict[Any, Any]:
        for field, value in values.items():
            if field in {"name", "ext", "size"} and value:
                print(
                    "Warning! "
                    f"{field}={value} will be overwritten during init."
                )
                values[field] = ""
        return values

    def __init__(self, **data: Any):
        super().__init__(**data)

        # Init fields
        self.name = self.path.name
        self.ext = self.path.suffix.lower()
        self.size = size_fmt(self.path.stat().st_size)


class File(FileInfo):
    encoding: Optional[int]
    parent_dirs: int = 0

    def get_file_outdir(self, outdir: Path) -> Path:
        return create_outdir(self.path, outdir, self.parent_dirs)


class FileConv(BaseModel):
    files: List[File]
    out_dir: Path
    convert_to: str
    max_errs: int = -1

    def __init__(self, **data: Any):
        super().__init__(**data)
        if self.max_errs < 0:
            self.max_errs = int(math.sqrt(len(self.files)))


# -----------------------------------------------------------------------------
# Function Definitions
# -----------------------------------------------------------------------------


def size_fmt(size: float) -> str:
    """Formats a file size in binary multiples to a human readable string.

    Parameters
    ----------
    size : float
        The file size in bytes.

    Returns
    -------
    str
        Human readable string representing size in binary multiples.
    """
    for unit in ["B", "KiB", "MiB", "GiB", "TiB"]:
        if size < 1024.0:
            break
        size /= 1024.0
    return f"{size:.1f} {unit}"


def create_outdir(file: Path, outdir: Path, parents: int = 0) -> Path:
    """Create the output directory for a file, where parents are the number of
    parents to use when naming the output directory.

    Parameters
    ----------
    file : Path
        The file for which to create an output directory.
    outdir : Path
        The current output directory.
    parents : int
        The number of parents to use when creating the output directory.
        Defaults to 0.

    Raises
    ------
    IndexError
        If the number of parents used for naming exceeds the number of actual
        parents a file has, and index error is thrown.
    """
    for i in range(parents, 0, -1):
        try:
            subdir = Path(f"{file}").parent.parts[-i]
        except IndexError:
            err_msg = f"Parent index {parents} out of range for {file}"
            raise IndexError(err_msg)
        else:
            outdir = outdir.joinpath(subdir)

    # Create the resulting output directory
    outdir.mkdir(parents=True, exist_ok=True)

    return outdir