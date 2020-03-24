"""Convertool internals.

"""
# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import math
from pathlib import Path
from typing import Any, List, Optional

from pydantic import BaseModel, validator

from convertool.utils import create_outdir

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
    checksum: Optional[str] = None
    identification: Optional[Identification] = None

    @validator("path")
    def path_must_be_file(cls, path: Path) -> Path:
        if not path.is_file():
            raise ValueError("File does not exist.")
        return path.resolve()

    @validator("name")
    def name_overwrite(cls, name: str) -> str:
        if name:
            print(f"Warning! name={name} will be overwritten during init.")
        return ""

    def __init__(self, **data: Any):
        super().__init__(**data)

        # Resolve path, init fields
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
    max_errs: Optional[int]

    def __init__(self, **data: Any):
        super().__init__(**data)
        if not self.max_errs:
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
