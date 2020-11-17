# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import platform
import subprocess

import pytest
from acamodels import ArchiveFile

import convertool.core.libreoffice as c_libre
from convertool.core.libreoffice import find_libre
from convertool.core.libreoffice import libre_convert
from convertool.exceptions import LibreError
from convertool.exceptions import LibreNotFoundError
from convertool.exceptions import ProcessError

# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------


@pytest.fixture
def test_file(test_docx) -> ArchiveFile:
    return ArchiveFile(path=test_docx)


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------


class TestLibreConvert:
    def test_valid_input(self, test_file, test_out):
        libre_convert(test_file, "odt", test_out)
        assert 61000 > (test_out / "test.odt").stat().st_size > 60000

    def test_process_error(self, test_file, test_out, monkeypatch):
        def proc_error(*args, **kwargs):
            raise ProcessError("fail")

        monkeypatch.setattr(c_libre, "run_proc", proc_error)
        err_match = r"Conversion of .* failed with error: fail"
        with pytest.raises(LibreError, match=err_match):
            libre_convert(test_file, "odt", test_out)

    def test_timeout_expired(self, test_file, test_out, monkeypatch):
        def timeout_exp(*args, **kwargs):
            raise subprocess.TimeoutExpired("convert", 1)

        monkeypatch.setattr(c_libre, "run_proc", timeout_exp)
        err_match = r"Conversion of .* timed out after 1 seconds."

        with pytest.raises(LibreError, match=err_match):
            libre_convert(test_file, "odt", test_out)


class TestFindLibre:
    def test_valid_input(self):
        # Running as expected
        assert find_libre()

    def test_system_exceptions(self, monkeypatch):
        # System check
        # We pretend subprocess.run() is always successful
        def completed_proc(*args, **kwargs):
            return subprocess.CompletedProcess(
                "exit 0", returncode=0, stdout=b"success"
            )

        monkeypatch.setattr(subprocess, "run", completed_proc)

        # Windows
        monkeypatch.setattr(platform, "system", lambda: "Windows")
        assert find_libre() == "success"
        # Linux
        monkeypatch.setattr(platform, "system", lambda: "Linux")
        assert find_libre() == "success"
        # Unsupported OS, raises LibreNotFoundError
        fail_os = "fail"
        monkeypatch.setattr(platform, "system", lambda: fail_os)
        with pytest.raises(
            LibreNotFoundError, match=f"OS {fail_os} not supported"
        ):
            find_libre()

    def test_process_error(self, monkeypatch):
        # CalledProcessError
        def called_proc_err(*args, **kwargs):
            raise subprocess.CalledProcessError(
                1, cmd="exit 1", stderr=b"proc fail"
            )

        monkeypatch.setattr(subprocess, "run", called_proc_err)
        err_match = "Could not find LibreOffice with error: proc fail"
        with pytest.raises(LibreNotFoundError, match=err_match):
            find_libre()
