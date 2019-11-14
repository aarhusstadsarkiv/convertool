"""Tool converting MS office documents to PDF using LibreOffice.

Windows and Linux compatible. Requires a LibreOffice installation via
chocolatey (Windows) or snap (Linux).

"""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import os
import sys
import platform
import subprocess
from subprocess import CalledProcessError
from typing import Optional

# -----------------------------------------------------------------------------
# Function Definitions
# -----------------------------------------------------------------------------


def find_libre(system: str) -> str:
    """Find the LibreOffice installation. This function is OS dependent, and
    will find either `libreoffice` on Linux, or `soffice.exe` on Windows, if
    these exist. If they do not, the program will exit with an error message
    from stderr.

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
                capture_output=True,
                check=True,
            )
            # Remove trailing newline and decode stdout from byte string.
            libre_path = cmd.stdout.rstrip().decode()
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
                ["which", "libreoffice"], capture_output=True, check=True
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


def convert(system: str) -> Optional[str]:
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

    Raises
    ------license" for more information.

>>> from os.path import abspath, realpath

>>> abspath('b')

    BadException
        description

    """
    script_path = os.path.dirname(os.path.realpath(__file__))
    file_dir = os.path.join(script_path, "files")
    outdir = os.path.join(script_path, "converted_files")
    libreoffice = find_libre(system)

    cmd = subprocess.run(
        f"{libreoffice} --headless --convert-to pdf {file_dir}/docx_test.docx --outdir {outdir}",
        shell=True,
        check=True,
    )
    return None


def main(system: str) -> Optional[str]:
    if system in ["Windows", "Linux"]:
        sys.exit(convert(system))
    else:
        exit_msg = (
            f"Expected to run on Windows or Linux, got {system} instead."
        )
        sys.exit(exit_msg)


if __name__ == "__main__":
    main(platform.system())
