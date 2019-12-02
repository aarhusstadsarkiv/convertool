"""Module level docstring.

"""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import time
from logging import Logger
from pathlib import Path
from typing import List, Optional
import tqdm
from .libreoffice import libre_convert
from .utils import log_setup, create_outdir, ACCEPTED_OUT
from .exceptions import LibreError, ConversionError

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
    ------
    BadException
        description

    """
    try:
        fsize = file.stat().st_size
    except FileNotFoundError:
        fsize = 0

    # Timeout is calculated as the base timeout + 1 second pr. MB.
    # We get the file size in whole MB by bit shifting by 20.
    timeout: int = base_timeout + (fsize >> 20)
    return timeout


def check_errors(err_count: int, max_errs: int) -> str:
    """Checks if more errors than the defined threshold has occurred, and
    returns a message describing the error if so.

    Parameters
    ----------
    err_count : int
        The current error count.
    max_errs : int
        The maximum amount of errors that are allowed to occur.

    Returns
    -------
    exit_msg : str
        A message describing the error, including information about the current
        number of errors and the maximum allowed amount. Empty if the error
        count has not yet exceeded the maximum allowed amount of errors.

    """
    exit_msg: str = ""

    if err_count > max_errs:
        exit_msg = f"Error count {err_count} is higher than "
        exit_msg += f"threshold of {max_errs}"

    return exit_msg


def convert_files(
    tool: str,
    files: List[str],
    outdir: str,
    convert_to: str,
    encoding: Optional[int] = None,
    parents: int = 0,
    max_errs: int = 0,
) -> None:
    """Convert a list of files and output the result to the specified output
    directory using a pre-specified tool. Optionally define the number of
    parent directories that must be used when outputting a resulting file.
    A maximum number of errors can be passed to this function, indicating
    how many tool specific errors that are acceptable before throwing a
    ConversionError.

    Parameters
    ----------
    tool : str
        The tool to use for conversion.
    files : List[str]
        A list of files to convert.
    outdir : str
        The path to which converted files should be saved.
    convert_to : str
        The file format to convert to.
    parents : int
        How many immediate parent directories to use for naming converted
        files. Defaults to 0.
    max_errs : int
        How many tool specific errors to accept before a ConversionError is
        thrown. Defaults to 0.

    Raises
    ------
    ConversionError
        When something goes wrong during conversion, a ConversionError is
        thrown. This happens if there are no files to convert; if the number
        of parents to use for naming is higher than the actual number of
        parents a file has in its path; and if too many tool specific errors
        occur.

    """
    # Initialise variables
    time_now: float = time.time()
    err_count: int = 0
    warn_count: int = 0
    log_msg: str

    # Set up logging
    logger: Logger = log_setup(
        log_name="Conversion",
        log_file=Path(outdir).joinpath(f"_convertool_{time_now}.log"),
    )

    # Check if output file format is supported
    if convert_to not in ACCEPTED_OUT:
        logger.error(f"Output to {convert_to} is not supported!")
        raise ConversionError(f"Output to {convert_to} is not supported!")

    # Start conversion.
    logger.info(f"Started conversion of {len(files)} files.")
    for file in tqdm.tqdm(files, desc="Converting files", unit="file"):

        # Create new output path based on parent naming.
        try:
            out_path: Path = create_outdir(Path(file), Path(outdir), parents)
        except IndexError as error:
            logger.error(error)
            raise ConversionError(error)

        # Convert with LibreOffice
        if tool == "libre":
            try:
                libre_convert(
                    f"{file}",
                    out_path,
                    convert_to,
                    encoding=encoding,
                    timeout=calc_timeout(Path(file)),
                )
            except LibreError as error:
                logger.warning(f"{error}")
                if not error.timeout:
                    err_count += 1
                else:
                    warn_count += 1
                errors: str = check_errors(err_count, max_errs)
                if errors:
                    logger.error(errors)
                    raise ConversionError(errors)

    # We are done! Log before we finish.
    log_msg = f"Finished conversion of {len(files)} files "
    log_msg += f"with {err_count + warn_count} issues, "
    log_msg += f"{err_count} of which were critical."
    logger.info(log_msg)
