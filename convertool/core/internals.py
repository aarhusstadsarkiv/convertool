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

from acamodels import ACABase
from acamodels import ArchiveFile
from pydantic import Field
from pydantic import validator


# -----------------------------------------------------------------------------
# Data Models
# -----------------------------------------------------------------------------


class FileConv(ACABase):
    files: List[ArchiveFile]
    out_dir: Path
    convert_to: str
    parent_dirs: int = 2
    max_errs: int = Field(None)

    # Validators
    @validator("max_errs", pre=True, always=True)
    def set_max_errs(
        cls, max_errs: Optional[int], values: Dict[str, Any]
    ) -> int:
        files = values.get("files") or []
        return max_errs or int(math.sqrt(len(files)))
