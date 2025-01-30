from os import PathLike
from pathlib import Path
from platform import system
from sqlite3 import DatabaseError
from subprocess import CalledProcessError
from subprocess import CompletedProcess
from subprocess import run
from tempfile import TemporaryDirectory

from acacore.database import FilesDB
from click import BadParameter
from click import Context
from click import Parameter

ENV: str = ""

if system().lower() in ("linux", "darwin"):
    ENV = "/usr/bin/env"


class AVIDDirs:
    def __init__(self, avid_dir: Path) -> None:
        self.dir: Path = avid_dir

    @property
    def original_documents(self):
        return self.dir / "OriginalDocuments"

    @property
    def master_documents(self):
        return self.dir / "MasterDocuments"

    @property
    def access_documents(self):
        return self.dir / "AccessDocuments"

    @property
    def documents(self):
        return self.dir / "Documents"


class AVID:
    def __init__(self, directory: str | PathLike) -> None:
        if not self.is_avid_dir(directory):
            raise ValueError(f"{directory} is not a valid AVID directory")

        self.path: Path = Path(directory).resolve()
        self.dirs: AVIDDirs = AVIDDirs(self.path)

    def __str__(self) -> str:
        return str(self.path)

    @classmethod
    def is_avid_dir(cls, directory: str | PathLike[str]) -> bool:
        directory = Path(directory)
        if not directory.is_dir():
            return False
        if not (avid_dirs := AVIDDirs(directory)).original_documents.is_dir() and not avid_dirs.documents.is_dir():  # noqa: SIM103
            return False
        return True

    @classmethod
    def find_database_root(cls, directory: str | PathLike[str]) -> Path | None:
        directory = Path(directory)
        if directory.joinpath("_metadata", "avid.db").is_file():
            return directory
        if directory.parent != directory:
            return cls.find_database_root(directory.parent)
        return None

    @property
    def metadata_dir(self):
        return self.path / "_metadata"

    @property
    def database_path(self):
        return self.metadata_dir / "avid.db"


def ctx_params(ctx: Context) -> dict[str, Parameter]:
    return {p.name: p for p in ctx.command.params}


def get_avid(ctx: Context, path: str | PathLike[str], param_name: str) -> AVID:
    if not AVID.is_avid_dir(path):
        raise BadParameter(f"Not a valid AVID directory {str(path)!r}.", ctx, ctx_params(ctx)[param_name])
    if not (avid := AVID(path)).database_path.is_file():
        raise BadParameter(
            f"No {avid.database_path.relative_to(avid.path)} present in {str(path)!r}.",
            ctx,
            ctx_params(ctx)[param_name],
        )
    return avid


def open_database(ctx: Context, avid: AVID, param_name: str) -> FilesDB:
    try:
        return FilesDB(avid.database_path, check_initialisation=True, check_version=True)
    except DatabaseError as e:
        raise BadParameter(e.args[0], ctx, ctx_params(ctx)[param_name])


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
            errors="replace",
            check=True,
            timeout=timeout,
        )
        return process.stdout or "", process.stderr or ""
    except FileNotFoundError:
        raise CalledProcessError(127, args[0:1], "", f"Command not found {''.join(args[0:1])}")


class TempDir(TemporaryDirectory):
    prefix: str = ".tmp_convertool_"

    def __init__(self, parent_dir: str | PathLike) -> None:
        super().__init__(dir=parent_dir, prefix=self.prefix)

    def __enter__(self) -> Path:
        return Path(self.name)
