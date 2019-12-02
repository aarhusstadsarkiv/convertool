"""Tool converting MS office documents to PDF using LibreOffice.

Windows and Linux compatible. Requires a LibreOffice installation via
chocolatey (Windows) or snap (Linux).

"""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import platform
import subprocess
from subprocess import CalledProcessError, TimeoutExpired
from pathlib import Path
from typing import Optional
from .utils import check_system, run_proc
from .exceptions import LibreError, ProcessError


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


def libre_convert(
    file: str,
    outdir: Path,
    convert_to: str,
    encoding: Optional[int] = None,
    cmd: str = find_libre(),
    timeout: int = 30,
) -> None:
    """Converts files in a file list to PDF using LibreOffice in headless mode.

    Parameters
    ----------
    files : List[str]
        List of paths to files to convert.
    outdir : str
        Directory where conversion results should be written to.
    convert_to : str
        The file type to convert to.
    encoding : Optional[int]
        Index for encoding to be used by LibreOffice. Only works for
        spreadsheet like files. Defaults to None.
    cmd : str
        Optional argument defining the path to the LibreOffice shell command or
        exe file. Defaults to
        :func:`~convertool.libreoffice.find_libre(platform.system())`
    timeout : int
        Optional argument defining the amount of seconds to wait for the
        LibreOffice command to finish. Defaults to 30.

    Raises
    ------
    LibreError
        If the LibreOffice CLI emits an error or times out, a LibreError is
        raised with a message detailing file name and reason, if any.
    """

    # Variables
    err_msg: str = ""

    cmd = f"{cmd} --headless --convert-to {convert_to}"

    # LibreOffice doesn't actually care what it gets in the infilter call;
    # if it doesn't find the filter you specify, it just uses the default.
    # As such, the convert command using --infilter will work no matter what
    # value encoding actually has. This doesn't seem particularly safe, so we
    # might want to type check the encoding input.
    if encoding is not None:
        convert_cmd = (
            f'{cmd} "{file}" --infilter=:{encoding} --outdir {outdir}'
        )
    else:
        convert_cmd = f'{cmd} "{file}" --outdir {outdir}'

    proc = subprocess.Popen(
        convert_cmd,
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )

    try:
        run_proc(proc, timeout=timeout)
    except ProcessError as error:
        err_msg = f"LibreConvert of {file} failed with error: {error}"
        raise LibreError(err_msg)
    except TimeoutExpired as error:
        err_msg = (
            f"LibreConvert of {file} timed out after {error.timeout} seconds."
        )
        raise LibreError(err_msg, timeout=True)
