"""Tool converting MS office documents to PDF using LibreOffice.

Windows and Linux compatible. Requires a LibreOffice installation via
chocolatey (Windows) or snap (Linux).

"""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import os
import sys
import subprocess
from subprocess import CalledProcessError
from typing import List
import tqdm  # type: ignore[import]

# -----------------------------------------------------------------------------
# Function Definitions
# -----------------------------------------------------------------------------


def find_libre(system: str) -> str:
    """Find the LibreOffice installation. This function is OS dependent, and
    will find either `libreoffice` on Linux, or `soffice.exe` on Windows, if
    these exist. If they do not, the program will exit with an error message
    from stderr retuned by subprocess.

    Parameters
    ----------
    system : str
        The current system from which the script is called.

    Returns
    -------
    libre_path : str
        Path to the LibreOffice executable or shell command needed to convert
        in headless mode.

    """

    libre_path: str = ""

    if system == "Windows":
        try:
            # Navigate to the program files folder, and try to find soffice.exe
            # recursively.
            cmd = subprocess.run(
                r"cd %programfiles% && where /r . *soffice.exe",
                shell=True,
                check=True,
                capture_output=True,
            )
            # Remove trailing newline and decode stdout from byte string.
            libre_path = '"' + cmd.stdout.rstrip().decode() + '"'
        except CalledProcessError as error:
            # Didn't find soffice.exe in the Program Files folder.
            # Return code != 0

            # Remove trailing newline and decode stderr from byte string.
            error_msg = error.stderr.rstrip().decode()

            exit_msg = f"Could not find LibreOffice with error: {error_msg}"
            sys.exit(exit_msg)
    elif system == "Linux":
        try:
            # Find the libreoffice shell command using which.
            cmd = subprocess.run(
                ["which", "libreoffice"], check=True, capture_output=True
            )
            # Remove trailing newline and decode stdout from byte string.
            libre_path = cmd.stdout.rstrip().decode()
        except CalledProcessError as error:
            # Didn't find the libreoffice shell command.
            # Return code != 0

            # Remove trailing newline and decode stderr from byte string.
            error_msg = error.stderr.rstrip().decode()

            exit_msg = f"Could not find LibreOffice with error: {error_msg}"
            sys.exit(exit_msg)

    return libre_path


def convert_files(system: str, files: List[str]) -> None:
    """Function level documentation.
    Delete non-applicable sections.

    Parameters
    ----------
    input : type
        description

    Returns
    -------
    return : type
        description
    type (anonymous types are allowed in return)
        description

    """
    script_path = os.path.dirname(os.path.realpath(__file__))
    outdir = os.path.join(script_path, "converted_files")
    libreoffice = find_libre(system)
    convert = r"--convert-to pdf"
    for file in tqdm.tqdm(files, desc="Converting files", unit="file"):
        try:
            cmd = subprocess.run(
                f"{libreoffice} --headless {convert} {file} --outdir {outdir}",
                shell=True,
                check=True,
                capture_output=True,
            )
            # If something goes wrong here, the process will sometimes exit
            # with code 0, but have a message in stderr. Thus, we need to
            # check stderr even though subprocess doesn't raise an error.
            error_msg = cmd.stderr.rstrip().decode()
            if error_msg:
                sys.exit(error_msg)
        except CalledProcessError as error:
            error_msg = error.stderr.rstrip().decode()
            exit_msg = f"Conversion failed with error: {error_msg}"
            sys.exit(exit_msg)
