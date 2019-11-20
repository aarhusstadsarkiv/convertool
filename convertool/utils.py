"""Utilities for handling files, paths, etc.

"""
# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import os
from typing import List
import tqdm

# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------


class WrongOSError(Exception):
    """Implements an error to raise when the OS is not supported."""


class ConversionError(Exception):
    """Implements an error to raise when conversion fails."""


class LibreError(Exception):
    """Implements an error to raise when LibreOffice or related
    functionality fails."""


# -----------------------------------------------------------------------------
# Function Definitions
# -----------------------------------------------------------------------------


def get_files(input_files: str) -> List[str]:
    """Finds files and empty directories in the given path,
    and collects them into a list of FileInfo objects.

    Parameters
    ----------
    files : str
        Directory of files, or text file with list of files to convert.

    Returns
    -------
    file_list : List[str]
        List of files to be converted.
    """
    # Type declarations
    file_list: List[str] = []

    # Traverse given path, collect results.
    # tqdm is used to show progress of os.walk
    if os.path.isdir(input_files):
        for root, _, files in tqdm.tqdm(os.walk(input_files, topdown=True)):
            for file in files:
                file_list.append(os.path.join(root, file))

    if os.path.isfile(input_files):
        with open(input_files) as in_file:
            for line in in_file.readlines():
                file_list.append(line.strip())

    return file_list


def check_system(system: str) -> None:
    """Checks if a given system is supported. Raises WrongOSError if not.

    Parameters
    ----------
    system : str
        The system on which the script is running.

    Raises
    ------
    WrongOSError
        If the system is not Windows or Linux, convertool will not work,
        and a WrongOSError is raised.
    """
    if system not in ["Windows", "Linux"]:
        raise WrongOSError(
            f"Expected to run on Windows or Linux, got {system}."
        )
