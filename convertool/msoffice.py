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
    find_libre_cmd: str = ""

    if system == "Windows":
        find_libre_cmd = r"cd %programfiles% && where /r . *soffice.exe"
    elif system == "Linux":
        find_libre_cmd = r"which libreoffice"
    else:
        exit_msg = f"Expected to run on Windows or Linux, got {system}."
        sys.exit(exit_msg)

    try:
        # Navigate to the program files folder, and try to find soffice.exe
        # recursively.
        cmd = subprocess.run(
            f"{find_libre_cmd}", shell=True, check=True, capture_output=True
        )
        # Remove trailing newline and decode stdout from byte string.
        # Windows needs the quotes.
        libre_path = f'"{cmd.stdout.strip().decode()}"'
    except CalledProcessError as error:
        # Didn't find executable or shell command.
        # Return code != 0

        # Remove trailing newline and decode stderr from byte string.
        error_msg = error.stderr.strip().decode()

        exit_msg = f"Could not find LibreOffice with error: {error_msg}"
        sys.exit(exit_msg)

    return libre_path


def convert_files(system: str, files: List[str], outdir: str) -> None:
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
    error_log: str = os.path.join(outdir, "convertool_log.txt")
    libreoffice = find_libre(system)
    convert = r"--headless --convert-to pdf"

    for file in tqdm.tqdm(files, desc="Converting files", unit="file"):
        # File names are weird! So we need to quote them.
        fname = f'"{file}"'
        try:
            cmd = subprocess.run(
                f"{libreoffice} {convert} {fname} --outdir {outdir}",
                shell=True,
                check=True,
                capture_output=True,
            )
            # If something goes wrong here, the process will sometimes exit
            # with code 0, but have a message in stderr. Thus, we need to
            # check stderr even though subprocess doesn't raise an error.
            # We let the process resume, but collect the errors to a log file.
            error_msg = cmd.stderr.strip().decode()
            if error_msg:
                log_msg = (
                    f"Conversion of {file} failed with error: {error_msg}\n"
                )
                with open(error_log, "a") as file:
                    file.write(log_msg)

        except CalledProcessError as error:
            error_msg = error.stderr.rstrip().decode()
            exit_msg = f"Conversion failed with error: {error_msg}"
            sys.exit(exit_msg)
