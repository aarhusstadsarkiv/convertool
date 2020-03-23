"""Convertool internals.

"""
# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import math
from pathlib import Path
from typing import Optional, List, Any
from pydantic import BaseModel, validator
from convertool.utils import create_outdir

# -----------------------------------------------------------------------------
# Globals
# -----------------------------------------------------------------------------
ACCEPTED_OUT = ["pdf", "ods", "odt", "odp", "html", "png", "tiff"]

# -----------------------------------------------------------------------------
# Data Models
# -----------------------------------------------------------------------------


class File(BaseModel):
    path: Path
    encoding: Optional[int]
    parent_dirs: int = 0

    def get_file_outdir(self, outdir: Path) -> Path:
        return create_outdir(self.path, outdir, self.parent_dirs)

    @validator("path")
    def path_must_be_file(cls, path: Path) -> Path:
        if not path.is_file():
            raise ValueError("File does not exist.")
        return path


class FileConv(BaseModel):
    files: List[File]
    max_errs: Optional[int]

    def __init__(self, **data: Any):
        super().__init__(**data)
        if not self.max_errs:
            self.max_errs = int(math.sqrt(len(self.files)))
