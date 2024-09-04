from os import PathLike
from pathlib import Path
from subprocess import CalledProcessError
from subprocess import CompletedProcess
from subprocess import run

from click import Context
from click import Parameter


def ctx_params(ctx: Context) -> dict[str, Parameter]:
    return {p.name: p for p in ctx.command.params}


def run_process(*args: str | int | PathLike, cwd: Path | None = None) -> tuple[str, str]:
    """
    :param args: The arguments for ``subprocess.run``. Non-string arguments are cast to string.
    :param cwd: Optionally, the working directory to use.
    :raise CalledProcessError: If the process exists with a non-zero code.
    :return: A tuple with the captured stdout and stderr outputs in string format.
    """
    try:
        process: CompletedProcess[str] = run(
            [*map(str, args)],
            cwd=cwd,
            capture_output=True,
            encoding="utf-8",
            check=True,
        )
        return process.stderr or "", process.stdout or ""
    except FileNotFoundError:
        raise CalledProcessError(127, args[0:1], "", f"Command not found {''.join(args[0:1])}")
