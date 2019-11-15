"""Utilities for handling files, paths, etc.

"""
# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import os
from typing import List

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
        for root, dirs, files in os.walk(input_files, topdown=True):
            print(dirs)
            for file in files:
                file_list.append(os.path.join(root, file))
    if os.path.isfile(input_files):
        with open(input_files) as in_file:
            for line in in_file.readlines():
                file_list.append(line.strip())

    return file_list
