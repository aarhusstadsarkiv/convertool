"""Utilities for handling files, paths, etc.

"""
# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import logging
from pathlib import Path
from subprocess import Popen
from subprocess import TimeoutExpired

from convertool.exceptions import ProcessError
from convertool.exceptions import WrongOSError

# -----------------------------------------------------------------------------
# Function Definitions
# -----------------------------------------------------------------------------


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


# def copy_file(file: Path, outdir: Path) -> None:
#     """Copies a file to the given output directory.

#      Parameters
#     ----------
#     file : Path
#         The file to copy.
#     outdir : Path
#         The output directory.
#     """
#     shutil.copy2(file, outdir)


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