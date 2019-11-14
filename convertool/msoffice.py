"""Tool converting MS office documents to PDF using LibreOffice.

Windows and Linux compatible. Requires a LibreOffice installation via
chocolatey (Windows) or snap (Linux).

"""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import sys
import subprocess
import platform

# -----------------------------------------------------------------------------
# Function Definitions
# -----------------------------------------------------------------------------


def find_libre(system: str) -> str:
    if system == "Windows":
        return subprocess.run(
            r"cd %programfiles% && where /r . *soffice.exe", shell=True
        )
    elif system == "Linux":
        return subprocess.run(["which", "libreoffice"])


def convert(system: str) -> None:
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
    ------
    BadException
        description

    """
    find_libre(system)


def main(system: str) -> None:
    if system in ["Windows", "Linux"]:
        return convert(system)
    return f"Expected to run on Windows or Linux, got {system} instead."


if __name__ == "__main__":
    sys.exit(main(platform.system()))
