"""Utilities for handling files, paths, etc.

"""
# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import logging as log
from logging import Logger
from pathlib import Path
from subprocess import Popen
from subprocess import TimeoutExpired

from convertool.exceptions import ProcessError

# -----------------------------------------------------------------------------
# Function Definitions
# -----------------------------------------------------------------------------


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


def log_setup(log_name: str, log_file: Path, mode: str = "a") -> Logger:
    """Creates a log with the name specified and outputs it to the
    specified path using write mode as default.

    Parameters
    ----------
    log_name : str
        The name of the log to be created
    log_file : pathlib.Path
        The file to log to
    mode : str
        How to write to the log file. Defaults to a.

    Returns
    -------
    logger : logging.Logger
        The resulting log handler
    """
    # Init & log to file
    logger: Logger = log.getLogger(log_name)
    file_handler = log.FileHandler(log_file, mode, encoding="utf-8")

    # Format
    log_fmt = log.Formatter(
        fmt="%(asctime)s %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(log_fmt)

    # Handler & level
    logger.addHandler(file_handler)
    logger.setLevel(log.INFO)

    return logger
