# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import platform
import subprocess
from pathlib import Path
from subprocess import CalledProcessError
from typing import List
from typing import Union

from acamodels import ArchiveFile

from convertool.exceptions import GSError
from convertool.exceptions import GSNotFoundError

# -----------------------------------------------------------------------------
# Conversion to PDF/A
# -----------------------------------------------------------------------------


def find_gs() -> str:
    gs_path: str
    gs_cmd: List[str]
    system: str = platform.system()

    if system == "Windows":
        gs_cmd = ["where.exe", "gswin64c.exe"]
    elif system in ["Linux", "Darwin"]:
        gs_cmd = ["which", "gs"]
    else:
        raise GSNotFoundError(f"OS {system} not supported")
    try:
        cmd = subprocess.run(gs_cmd, check=True, capture_output=True)
    except CalledProcessError as error:
        raise GSNotFoundError(
            "Could not find Ghostscript with error: "
            f"{error.stderr.strip().decode()}"
        )
    else:
        gs_path = cmd.stdout.strip().decode()

    return gs_path


def convert_pdf(file: ArchiveFile, outdir: Path) -> None:
    gs: str = find_gs()
    # GS uses % in sOutputFile for printer information
    # and will crash if % is present in the file name
    out_file = outdir / "out.pdf"
    cmd: List[Union[str, Path]] = [
        gs,
        "-dBATCH",
        "-dNOPAUSE",
        "-dPDFA=3",
        "-dPDFACompatibilityPolicy=1",
        "-sDEVICE=pdfwrite",
        "-sColorConversionStrategy=UseDeviceIndependentColor",
        f"-sOutputFile={out_file}",
        file.path,
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except CalledProcessError as error:
        raise GSError(
            f"Conversion of {file.path} failed "
            f"with error: {error.stderr.strip().decode()}"
        )
    else:
        new_name = out_file.with_name(file.path.name).with_suffix(".pdf")
        out_file.rename(new_name)
