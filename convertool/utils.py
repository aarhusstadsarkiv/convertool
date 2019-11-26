"""Utilities for handling files, paths, etc.

"""
# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import os
from subprocess import Popen, TimeoutExpired
from typing import List
import tqdm

# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------


class WrongOSError(Exception):
    """Implements an error to raise when the OS is not supported."""


class CriticalProcessError(Exception):
    """Implements an error to raise when a process exits with code != 0"""


class ProcessError(Exception):
    """Implements an error to raise when a process has messages in stderr"""


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


def run_proc(proc: Popen, timeout: int) -> None:
    """Runs a Popen process with a given timeout. Kills the process and raises
    TimeoutExpired if the process does not finish within timeout in seconds. If
    there are messages in stderr, these are collected and a ProcessError is
    raised.

    Parameters
    ----------
    proc : subprocess.Popen
        The proc to communicate with.
    timeout : int
        Number of seconds before timeput.

    Raises
    ------
    TimeoutExpired
        If communication with the process fails to terminate within timeout
        seconds, the process is killed and TimeoutExpired is raised.
    CriticalProcessError
        If the process terminates within timeout seconds, but has exit code
        not equal to 0, a CriticalProcessError is raised.
    ProcessError
        If the process terminates within timeout seconds, but has messages in
        stderr and exit code 0, a ProcessError is raised.
    """
    try:
        # Communicate with process, collect stderr
        _, errs = proc.communicate(timeout=timeout)
    except TimeoutExpired:
        # Process timed out. Kill and re-raise.
        proc.kill()
        raise
    else:
        exit_code = proc.returncode
        err_msg = ""
        if errs:
            err_msg = errs.strip().decode()

        if exit_code != 0:
            if not err_msg:
                # There is nothing in stderr :(
                err_msg = f"Exited with code {exit_code} and empty stderr"
            raise CriticalProcessError(err_msg)
        elif err_msg:
            # Got something in stderr with exit code = 0. Decode and raise.
            raise ProcessError(err_msg)
