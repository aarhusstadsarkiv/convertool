"""Utilities for handling files, paths, etc.

"""
# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import os
import logging
from pathlib import Path
from subprocess import Popen, TimeoutExpired
from typing import List
import tqdm
from .exceptions import WrongOSError, ProcessError

# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------


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


def create_outdir(file: Path, outdir: Path, parents: int = 0) -> Path:
    """Create the output directory for a file, where parents are the number of
    parents to use when naming the output directory.

    Parameters
    ----------
    file : Path
        The file for which to create an output directory.
    outdir : Path
        The current output directory.
    parents : int
        The number of parents to use when creating the output directory.
        Defaults to 0.

    Raises
    ------
    IndexError
        If the number of parents used for naming exceeds the number of actual
        parents a file has, and index error is thrown.
    """
    for i in range(parents, 0, -1):
        try:
            subdir = Path(f"{file}").parent.parts[-i]
        except IndexError:
            err_msg = f"Parent index {parents} out of range for {file}"
            raise IndexError(err_msg)
        else:
            outdir = outdir.joinpath(subdir)

    return outdir


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
    ProcessError
        If the process terminates within timeout seconds, but has messages in
        stderr and/or exit code != 0, a ProcessError is raised.
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

        # Check stderr/exit code from process call.
        if errs:
            err_msg = errs.strip().decode()
        elif exit_code != 0:
            # Fail with nothing in stderr :(
            err_msg = f"Exited with code {exit_code} and empty stderr"

        if err_msg:
            raise ProcessError(err_msg)


def log_setup(
    log_name: str, log_file: Path, mode: str = "w"
) -> logging.Logger:
    logger = logging.getLogger(log_name)
    file_handler = logging.FileHandler(log_file, mode)
    file_handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s %(levelname)s: %(message)s", datefmt="%H:%M:%S"
        )
    )
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)
    return logger
