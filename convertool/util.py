from os import PathLike
from pathlib import Path
from platform import system
from subprocess import CalledProcessError
from subprocess import CompletedProcess
from subprocess import run

from click import Context
from click import Parameter

ENV: str = ""

if system().lower() in ("linux", "darwin"):
    ENV = "/usr/bin/env"


def ctx_params(ctx: Context) -> dict[str, Parameter]:
    return {p.name: p for p in ctx.command.params}


def run_process(*args: str | int | PathLike, cwd: Path | None = None, env: bool = True) -> tuple[str, str]:
    """
    Run process and capture output.

    If the command is not found, a ``CalledProcessError`` exception is raised instead of ``FileNotFoundError``.

    :param args: The arguments for ``subprocess.run``. Non-string arguments are cast to string.
    :param cwd: Optionally, the working directory to use.
    :param env: If ``True`` to use the system's env command (if available)
    :raise CalledProcessError: If the process exists with a non-zero code.
    :return: A tuple with the captured stdout and stderr outputs in string format.
    """
    try:
        env_args = [ENV] if env and ENV else []
        process: CompletedProcess[str] = run(
            [*env_args, *map(str, args)],
            cwd=cwd,
            capture_output=True,
            encoding="utf-8",
            check=True,
        )
        return process.stderr or "", process.stdout or ""
    except FileNotFoundError:
        raise CalledProcessError(127, args[0:1], "", f"Command not found {''.join(args[0:1])}")
