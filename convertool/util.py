from os import PathLike
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


def run_process(
    *args: str | int | PathLike,
    cwd: str | PathLike | None = None,
    env: bool = True,
    capture_output: bool = True,
    timeout: float | None = None,
) -> tuple[str, str]:
    """
    Run process and capture output.

    If the command is not found, a ``CalledProcessError`` exception is raised instead of ``FileNotFoundError``.

    :param args: The arguments for ``subprocess.run``. Non-string arguments are cast to string.
    :param cwd: Optionally, the working directory to use.
    :param env: If ``True`` to use the system's env command (if available).
    :param capture_output: Whether to capture the output of ``subprocess.run``. Default: ``True``.
    :param timeout: Optionally, a timeout.
    :raise CalledProcessError: If the process exists with a non-zero code.
    :raise TimeoutExpired: If the process times out.
    :return: A tuple with the captured stdout and stderr outputs in string format.
    """
    try:
        env_args = [ENV] if env and ENV else []
        process: CompletedProcess[str] = run(
            [*env_args, *map(str, args)],
            cwd=cwd,
            capture_output=capture_output,
            encoding="utf-8",
            check=True,
            timeout=timeout,
        )
        return process.stderr or "", process.stdout or ""
    except FileNotFoundError:
        raise CalledProcessError(127, args[0:1], "", f"Command not found {''.join(args[0:1])}")
