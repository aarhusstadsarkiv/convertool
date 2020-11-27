"""Tool converting MS office documents to PDF using LibreOffice.

Windows and Linux compatible. Requires a LibreOffice installation via
chocolatey (Windows) or snap (Linux).

"""
# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import platform
import subprocess
from pathlib import Path
from subprocess import CalledProcessError
from subprocess import TimeoutExpired
from typing import List
from typing import Union

from acamodels import ArchiveFile

from .utils import run_proc
from convertool.exceptions import LibreError
from convertool.exceptions import LibreNotFoundError
from convertool.exceptions import ProcessError

# -----------------------------------------------------------------------------
# Function Definitions
# -----------------------------------------------------------------------------


def find_libre() -> str:
    """Find the LibreOffice installation.

    Returns
    -------
    libre_path : str
        Path to the LibreOffice executable or shell command needed to convert
        in headless mode.

    Raises
    ------
    LibreError
        If the command to find LibreOffice on the current system fails,
        a LibreError is raised.

    """

    libre_path: str
    libre_cmd: List[str]
    system: str = platform.system()

    if system == "Windows":
        libre_cmd = ["where.exe", "*soffice.exe"]
    elif system in ["Linux", "Darwin"]:
        libre_cmd = ["which", "libreoffice"]
    else:
        raise LibreNotFoundError(f"OS {system} not supported")

    try:
        cmd = subprocess.run(libre_cmd, check=True, capture_output=True)
    except CalledProcessError as error:
        raise LibreNotFoundError(
            "Could not find LibreOffice with error: "
            f"{error.stderr.strip().decode()}"
        )
    else:
        # Remove trailing newline and decode stdout from byte string.
        # Windows needs the quotes.
        libre_path = cmd.stdout.strip().decode()

    return libre_path


def libre_convert(
    file: ArchiveFile,
    convert_to: str,
    outdir: Path,
    timeout: int = 30,
) -> None:
    """Converts files in a file list to PDF using LibreOffice in headless mode.

    Parameters
    ----------
    file : str
        File to convert
    outdir : str
        Directory where conversion results should be written to.
    convert_to : str
        The file type to convert to.
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
    err_msg: str
    libre_path: str = find_libre()
    cmd: List[Union[str, Path]] = [
        libre_path,
        "--headless",
        "--convert-to",
        convert_to,
        file.path,
        "--outdir",
        outdir,
    ]

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    try:
        run_proc(proc, timeout=timeout)
    except ProcessError as error:
        proc.kill()
        raise LibreError(
            f"Conversion of {file.path} failed with error: {error}"
        )
    except TimeoutExpired as error:
        proc.kill()
        _, _ = proc.communicate()
        err_msg = (
            f"Conversion of {file.path} "
            f"timed out after {error.timeout} seconds."
        )
        raise LibreError(err_msg, timeout=True)
