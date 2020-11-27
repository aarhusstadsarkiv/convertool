# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import platform
import subprocess

import pytest
from acamodels import ArchiveFile

from convertool.core import pdf as c_pdf
from convertool.core.pdf import convert_pdf
from convertool.core.pdf import find_gs
from convertool.exceptions import GSError
from convertool.exceptions import GSNotFoundError

# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------


@pytest.fixture
def test_file(test_pdf) -> ArchiveFile:
    return ArchiveFile(path=test_pdf)


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------


class TestFindGS:
    def test_valid_input(self):
        assert find_gs()

    def test_os_exceptions(self, monkeypatch):
        # System check
        # We pretend subprocess.run() is always successful
        def completed_proc(*args, **kwargs):
            return subprocess.CompletedProcess(
                "exit 0", returncode=0, stdout=b"success"
            )

        monkeypatch.setattr(subprocess, "run", completed_proc)

        # Windows
        monkeypatch.setattr(platform, "system", lambda: "Windows")
        assert find_gs() == "success"

        # Linux
        monkeypatch.setattr(platform, "system", lambda: "Linux")
        assert find_gs() == "success"

        # Unsupported OS, raises GSNotFoundError
        fail_os = "fail"
        monkeypatch.setattr(platform, "system", lambda: fail_os)
        with pytest.raises(
            GSNotFoundError, match=f"OS {fail_os} not supported"
        ):
            find_gs()

    def test_process_error(self, monkeypatch):
        # CalledProcessError
        def called_proc_err(*args, **kwargs):
            raise subprocess.CalledProcessError(
                1, cmd="exit 1", stderr=b"proc fail"
            )

        monkeypatch.setattr(subprocess, "run", called_proc_err)
        err_match = "Could not find Ghostscript with error: proc fail"
        with pytest.raises(GSNotFoundError, match=err_match):
            find_gs()


class TestConvertGS:
    def test_valid_input(self, test_file, test_out):
        convert_pdf(test_file, test_out)
        assert 62000 > (test_out / "test.pdf").stat().st_size > 61000

    def test_process_error(self, test_file, test_out, monkeypatch):
        # CalledProcessError
        def called_proc_err(*args, **kwargs):
            raise subprocess.CalledProcessError(
                1, cmd="exit 1", stderr=b"proc fail"
            )

        monkeypatch.setattr(c_pdf, "find_gs", lambda *args: "nice_path")
        monkeypatch.setattr(subprocess, "run", called_proc_err)
        err_match = r"Conversion of .* failed with error: proc fail"
        with pytest.raises(GSError, match=err_match):
            convert_pdf(test_file, test_out)
