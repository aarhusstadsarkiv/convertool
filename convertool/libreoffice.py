"""Tool converting MS office documents to PDF using LibreOffice.

Windows and Linux compatible. Requires a LibreOffice installation via
chocolatey (Windows) or snap (Linux).

"""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import os
import math
import platform
import logging
import subprocess
from subprocess import CalledProcessError, TimeoutExpired
from pathlib import Path
from typing import List
import tqdm
import humanize
from .utils import check_system, run_proc, ProcessError, CriticalProcessError

# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------


class ConversionError(Exception):
    """Implements an error to raise when conversion fails."""


class LibreError(Exception):
    """Implements an error to raise when LibreOffice or related
    functionality fails."""


# -----------------------------------------------------------------------------
# Function Definitions
# -----------------------------------------------------------------------------


def find_libre(system: str = platform.system()) -> str:
    """Find the LibreOffice installation. This function is OS dependent, and
    will find either `libreoffice` on Linux, or `soffice.exe` on Windows, if
    these exist. If they do not, an exception is raised and the CLI will exit
    with an error code.

    Parameters
    ----------
    system : str
        The current system from which the script is called.

    Returns
    -------
    libre_path : str
        Path to the LibreOffice executable or shell command needed to convert
        in headless mode.

    Raises
    ------
    WrongOSError
        If there is an attempt to find LibreOffice on a system that is not
        either Windows or Linux, a WrongOSError is raised from
        :func:`~convertool.utils.check_system()`.
    LibreError
        If the command to find LibreOffice on the current system fails,
        a LibreError is raised.

    """

    libre_path: str = ""
    find_libre_cmd: str = ""

    check_system(system)

    if system == "Windows":
        find_libre_cmd = r"cd %programfiles% && where /r . *soffice.exe"
    elif system == "Linux":
        find_libre_cmd = r"which libreoffice"

    try:
        # Invoke the OS specific command to find libreoffice.
        cmd = subprocess.run(
            f"{find_libre_cmd}", shell=True, check=True, capture_output=True
        )
    except CalledProcessError as error:
        # Didn't find executable or shell command.
        # Return code != 0
        error_msg = error.stderr.strip().decode()
        exit_msg = f"Could not find LibreOffice with error: {error_msg}"
        raise LibreError(exit_msg)
    else:
        # Remove trailing newline and decode stdout from byte string.
        # Windows needs the quotes.
        libre_path = f'"{cmd.stdout.strip().decode()}"'
        # libre_path = f"{cmd.stdout.strip().decode()}"

    return libre_path


def convert_files(
    files: List[str],
    outdir: str,
    pname: int = 0,
    libre: str = find_libre(),
    timeout: int = 30,
) -> None:
    """Converts files in a file list to PDF using LibreOffice in headless mode.

    Parameters
    ----------
    files : List[str]
        List of paths to files to convert.
    outdir : str
        Directory where conversion results should be written to.
    pname : int
        Number of parent directories to use in file naming. Defaults to 0.
    libre : str
        Optional argument defining the path to the LibreOffice shell command or
        exe file. Defaults to
        :func:`~convertool.libreoffice.find_libre(platform.system())`
    timeout : int
        Optional argument defining the amount of seconds to wait for the
        LibreOffice command to finish. Defaults to 30.

    Raises
    ------
    ConversionError
        If LibreOffice conversion fails a sufficient amount of times, a
        a ConversionError is raised, because too many errors were encountered.

    """
    # Set up logging
    error_log: str = os.path.join(outdir, "_convertool.log")
    logging.basicConfig(
        filename=error_log,
        format="%(asctime)s %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
        filemode="w",
        level=logging.INFO,
    )
    # Counter to keep track of errors
    err_count: int = 0
    threshold: int = round(math.log(len(files)))
    file_errs: int = 0
    convert = r"--headless --convert-to pdf"

    # Log and start file conversion
    logging.info(f"Starting conversion of {len(files)} files.")
    for file in tqdm.tqdm(files, desc="Converting files", unit="file"):
        out = Path(outdir)
        fname = f'"{file}"'
        for i in range(pname, 0, -1):
            try:
                out = out.joinpath(Path(fname).parent.parts[-i])
            except IndexError:
                err_msg = f"Parent index {pname} out of range for {file}"
                raise ConversionError(err_msg)
        proc = subprocess.Popen(
            f"{libre} {convert} {fname} --outdir {out}",
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        try:
            run_proc(proc, timeout=timeout)
        except TimeoutExpired as error:
            time = f"{error.timeout} seconds"
            file_errs += 1
            fsize = humanize.naturalsize(os.stat(file).st_size)
            logging.warning(
                f"Conversion of {file} ({fsize}) timed out after {time}"
            )
        except ProcessError as error:
            file_errs += 1
            logging.warning(f"Conversion of {file} failed with error {error}")
        except CriticalProcessError as error:
            err_count += 1
            file_errs += 1
            logging.warning(f"Conversion of {file} failed with error {error}")
            if err_count > threshold:
                logging.warning(
                    f"Error count {err_count} is over threshold of {threshold}"
                )
                raise ConversionError("Too many errors encountered.")

    # Log that we're done
    log_msg = (
        f"Finished converting {len(files)} files with {file_errs} errors, "
    )
    log_msg += f"{err_count} of which were critical."
    logging.info(log_msg)
