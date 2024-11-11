from pathlib import Path
from subprocess import CalledProcessError
from subprocess import TimeoutExpired

import pytest

from convertool.util import run_process
from convertool.util import TempDir


def test_run_process(output_dir: Path):
    out, err = run_process("echo", "hello")
    assert out == "hello\n"
    assert err == ""

    out, err = run_process("pwd", cwd=output_dir)
    assert out == f"{output_dir}\n"
    assert err == ""

    with pytest.raises(CalledProcessError) as exception:
        run_process("stat", output_dir / "__nonexisting_file")
    assert exception.value.stderr.startswith("stat: ")

    with pytest.raises(CalledProcessError) as exception:
        run_process("__nonexisting_command", env=False)
    assert exception.value.stderr.lower() == "command not found __nonexisting_command"

    with pytest.raises(TimeoutExpired):
        run_process("sleep", 1, timeout=0.1)


def test_temporary_directory(output_dir: Path):
    with TempDir(output_dir) as temp_dir:
        assert temp_dir.is_dir()
        assert temp_dir.name.startswith(TempDir.prefix)
    assert not temp_dir.is_dir()
