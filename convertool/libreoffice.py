"""Tool converting MS office documents to PDF using LibreOffice.

Windows and Linux compatible. Requires a LibreOffice installation via
chocolatey (Windows) or snap (Linux).

"""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import os
import subprocess
import platform
from subprocess import CalledProcessError
from typing import List
import tqdm
from .utils import check_system, WrongOSError, ConversionError, LibreError


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
        either Windows or Linux, a WrongOSError is raised.
    LibreError
        If the command to find LibreOffice on the current system fails,
        a LibreError is raised.

    """

    libre_path: str = ""
    find_libre_cmd: str = ""

    try:
        check_system(system)
    except WrongOSError:
        raise
    else:
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

    return libre_path


def convert_files(
    files: List[str], outdir: str, libre: str = find_libre()
) -> None:
    """Converts files in a file list to PDF using LibreOffice in headless mode.

    Parameters
    ----------
    files: List[str]
        List of paths to files to convert.
    outdir: str
        Directory where conversion results should be written to.
    libre: str
        Optional argument defining the path to the LibreOffice shell command or
        exe file. Defaults to
        :func:`~convertool.libreoffice.find_libre(platform.system())`

    Raises
    ------
    ConversionError
        If something goes wrong in the LibreOffice convert step,
        a ConversionError is raised with a message specifying file
        and error from LibreOffice, if applicable.

    """
    error_log: str = os.path.join(outdir, "_convertool_log.txt")
    convert = r"--headless --convert-to pdf"

    for file in tqdm.tqdm(files, desc="Converting files", unit="file"):
        # File names are weird! So we need to quote them.
        fname = f'"{file}"'
        try:
            cmd = subprocess.run(
                f"{libre} {convert} {fname} --outdir {outdir}",
                shell=True,
                check=True,
                capture_output=True,
            )
        except CalledProcessError as error:
            error_msg = error.stderr.rstrip().decode()
            return_code = error.returncode

            # LibreOffice sometimes fails without a message in stderr.
            if not error_msg:
                error_msg = (
                    f"Unspecified LibreOffice error: Return code {return_code}"
                )

            # Log and raise
            exit_msg = f"Conversion of {file} failed with error: {error_msg}"
            with open(error_log, "a") as file:
                file.write(f"{exit_msg}\n")
            raise ConversionError(exit_msg)
        else:
            # If something goes wrong here, the process will sometimes exit
            # with code 0, but have a message in stderr. Thus, we need to
            # check stderr even though subprocess doesn't raise an error.
            # We let the process resume, but collect the errors to a log file.
            stderr_msg = cmd.stderr.strip().decode()
            if stderr_msg:
                log_msg = (
                    f"Conversion of {file} failed with error: {stderr_msg}\n"
                )
                with open(error_log, "a") as file:
                    file.write(log_msg)
