"""Convertool internals.

"""
# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import math
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from acamodels import ArchiveFile
from pydantic import BaseModel
from pydantic import Field
from pydantic import validator

# -----------------------------------------------------------------------------
# Globals
# -----------------------------------------------------------------------------
ACCEPTED_OUT = ["pdf", "ods", "odt", "odp", "html", "png", "tiff"]

# -----------------------------------------------------------------------------
# Data Models
# -----------------------------------------------------------------------------


class File(ArchiveFile):
    encoding: Optional[int]
    parent_dirs: int = 0

    def get_file_outdir(self, outdir: Path) -> Path:
        return create_outdir(self.path, outdir, self.parent_dirs)


class FileConv(BaseModel):
    files: List[File]
    out_dir: Path
    convert_to: str
    max_errs: int = Field(None)

    @validator("max_errs", pre=True, always=True)
    def set_max_errs(
        cls, max_errs: Optional[int], values: Dict[str, Any]
    ) -> int:
        files = values.get("files") or []
        return max_errs or int(math.sqrt(len(files)))


# -----------------------------------------------------------------------------
# Function Definitions
# -----------------------------------------------------------------------------


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
