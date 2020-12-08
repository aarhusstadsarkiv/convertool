"""Module level docstring.

"""
# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import json
import math
from logging import Logger
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import tqdm
from acamodels import ACABase
from acamodels import ArchiveFile
from pydantic import Field
from pydantic import validator

from .image import img2tif
from .libreoffice import libre_convert
from .pdf import convert_pdf
from .utils import log_setup
from convertool.database import FileDB
from convertool.exceptions import ConversionError
from convertool.exceptions import GSError
from convertool.exceptions import ImageError
from convertool.exceptions import LibreError

# import shutil


# -----------------------------------------------------------------------------
# FileConv Model
# -----------------------------------------------------------------------------


class FileConv(ACABase):
    files: List[ArchiveFile]
    db: FileDB
    out_dir: Path
    max_errs: int = Field(None)

    class Config:
        arbitrary_types_allowed = True

    # Validators
    @validator("max_errs", pre=True, always=True)
    def set_max_errs(
        cls, max_errs: Optional[int], values: Dict[str, Any]
    ) -> int:
        files = values.get("files") or []
        return max_errs or int(math.sqrt(len(files)))

    @staticmethod
    def conv_map() -> Dict[str, str]:
        map_file = Path(__file__).parent / "convert_map.json"
        with map_file.open(encoding="utf-8") as f:
            c_map: Dict[str, str] = json.load(f)
            return c_map

    async def convert(self) -> None:
        # Initialise variables
        err_count: int = 0
        warn_count: int = 0
        convert_to: Optional[str]

        # Set up logging
        logger: Logger = log_setup(
            log_name="Conversion",
            log_file=Path(self.out_dir) / "_convertool.log",
        )
        converted_uuids = await self.db.converted_uuids()
        to_convert: List[ArchiveFile] = [
            f
            for f in self.files
            if f.puid in self.conv_map() and f.uuid not in converted_uuids
        ]
        # Start conversion.
        logger.info(
            f"Started conversion of {len(to_convert)} files "
            f"from {self.db.url} to {self.out_dir}"
        )
        for file in tqdm.tqdm(
            to_convert, desc="Converting files", unit="file"
        ):
            # Create output directory
            file_out: Path = self.out_dir / file.aars_path.parent
            file_out.mkdir(parents=True, exist_ok=True)

            # Convert info
            convert_to = self.conv_map().get(file.puid)

            if convert_to in ["odt", "ods", "odp"]:
                timeout = calc_timeout(file.path)
                logger.info(f"Starting conversion of {file.path}")
                try:
                    libre_convert(file, convert_to, file_out, timeout=timeout)
                except LibreError as error:
                    logger.warning(f"Failed to convert {file.path}: {error}")
                    if error.timeout:
                        warn_count += 1
                    else:
                        err_count += 1
                else:
                    await self.db.update_status(file.uuid)
                    logger.info(f"Converted {file.path} successfully.")

            if convert_to == "pdf":
                logger.info(f"Starting conversion of {file.path}")
                try:
                    convert_pdf(file, file_out)
                except GSError as error:
                    logger.warning(f"Failed to convert {file.path}: {error}")
                    err_count += 1
                else:
                    await self.db.update_status(file.uuid)
                    logger.info(f"Converted {file.path} successfully.")

            if convert_to == "tif":
                logger.info(f"Starting conversion of {file.path}")
                try:
                    img2tif(file.path, file_out)
                except ImageError as error:
                    logger.warning(f"Failed to convert {file.path}: {error}")
                    err_count += 1
                else:
                    await self.db.update_status(file.uuid)
                    logger.info(f"Converted {file.path} successfully.")

            # Check if too many errors have occurred.
            if err_count > self.max_errs:
                msg = (
                    f"Error count {err_count} is higher than "
                    f"threshold of {self.max_errs}"
                )
                logger.error(msg)
                raise ConversionError(msg)

        # We are done! Log before we finish.
        logger.info(
            f"Finished conversion of {len(to_convert)} files "
            f"with {err_count + warn_count} issues, "
            f"{err_count} of which were critical."
        )


# -----------------------------------------------------------------------------
# Function Definitions
# -----------------------------------------------------------------------------


def calc_timeout(file: Path, base_timeout: int = 10) -> int:
    """Calculates a timeout value based on file size and a base timeout.

    Parameters
    ----------
    file : Path
        The file from which timeout should be calculated.
    base_timeout : int
        The base timeout. Defaults to 10.

    Returns
    -------
    timeout : int
        The timeout calculated as the base timeout plus file size in whole MBs.
        Essentially, a file gets 1 second extra per MB.
    """

    fsize: int
    try:
        fsize = file.stat().st_size
    except FileNotFoundError:
        fsize = 0

    # Timeout is calculated as the base timeout + 1 second pr. MB.
    # We get the file size in whole MB by bit shifting by 20.
    timeout: int = base_timeout + (fsize >> 20)
    return timeout
