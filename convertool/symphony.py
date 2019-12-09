"""Tool for converting LWP files to ODT.
"""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import platform
import time
import subprocess
from subprocess import CalledProcessError
from pathlib import Path
import pyautogui
import pyperclip
from convertool.exceptions import SymphonyError, WrongOSError

# -----------------------------------------------------------------------------
# Globals
# -----------------------------------------------------------------------------
pyautogui.PAUSE = 0.3

# -----------------------------------------------------------------------------
# Function Definitions
# -----------------------------------------------------------------------------


def copypaste(str_to_copy: str) -> None:
    pyperclip.copy(f"{str_to_copy}")
    pyautogui.hotkey("ctrl", "v")
    pyautogui.press("enter")


def save_as(file: str) -> None:
    pyautogui.hotkey("ctrl", "shift", "s", interval=0.1)
    copypaste(file)


def find_symphony(system: str = platform.system()) -> str:

    # Initialise variables
    exe_path: str = ""

    # System specific functionality.
    if system == "Windows":
        find_symphony_cmd = (
            r"cd %programfiles(x86)% && where /r . symphony.exe"
        )
    else:
        raise WrongOSError(
            f"Conversion using IBM Symphony is not supported on {system}."
        )

    # Invoke the command to find Symphony on Windows.
    try:
        cmd = subprocess.run(
            f"{find_symphony_cmd}", shell=True, check=True, capture_output=True
        )
    except CalledProcessError as error:
        # Didn't find executable.
        # Return code != 0
        error_msg = error.stderr.strip().decode()
        raise SymphonyError(
            f"Could not find IBM Symphony with error: {error_msg}"
        )
    else:
        # Remove trailing newline and decode stdout from byte string.
        # Windows needs the quotes. IBM Symphony has more than one exe file
        # after install. Finger's crossed the correct one is always the first
        # Windows finds. :|
        exe_path = f'"{cmd.stdout.strip().decode().splitlines()[0]}"'
        return exe_path


def symphony_convert(file: Path, outdir: Path) -> None:
    # Initialise variables
    cmd: str = find_symphony()
    outfile: Path = outdir.joinpath(f"{file.stem}.odt")

    # If outfile exists, delete it first.
    if outfile.is_file():
        outfile.unlink()

    # Open IBM Symphony and do unholy things with pyautogui
    try:
        subprocess.run(cmd, shell=True, check=True)
    except CalledProcessError as error:
        error_msg = error.stderr.strip().decode()
        raise SymphonyError(
            f"Execution of IBM Symphony failed with error: {error_msg}"
        )
    else:
        # Wait a bit, then open the file
        time.sleep(1)
        pyautogui.hotkey("ctrl", "o")
        copypaste(str(file))

        # Symphony opens an extra menu when ctrl+o is used for... reasons.
        # Esc closes it.
        pyautogui.press("escape")
        time.sleep(1)

        # Save the file as ODT.
        save_as(str(outfile))
        time.sleep(0.25)

        # Kill Symphony
        subprocess.run(
            "taskkill /f /im symphony*", shell=True, capture_output=True
        )
        subprocess.run(
            "taskkill /f /im soffice*", shell=True, capture_output=True
        )
        time.sleep(0.1)

        # If outfile does not exist after the above, we probably have a
        # problem.
        if not outfile.is_file():
            raise SymphonyError(f"Conversion of {file} failed!")
