# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import sys
from pathlib import Path
from subprocess import PIPE
from subprocess import Popen
from subprocess import TimeoutExpired

import pytest

from convertool.exceptions import ProcessError
from convertool.exceptions import WrongOSError
from convertool.utils import check_system
from convertool.utils import create_outdir
from convertool.utils import run_proc


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------


class TestCheckSystem:
    def test_with_correct_system(self):
        try:
            check_system("Windows")
            check_system("Linux")
        except WrongOSError:
            pytest.fail("Unexpected WrongOSError!")

    def test_with_incorrect_system(self):
        with pytest.raises(WrongOSError):
            check_system("Bogus")


class TestCreateOutdir:
    def test_with_parent_in_range(self, test_pdf, temp_dir):
        outdir = Path(temp_dir, "temp_out")
        assert (
            create_outdir(test_pdf, outdir, 1)
            == outdir / Path(test_pdf).parent.parts[-1]
        )

    def test_with_parent_out_of_range(self, test_pdf, temp_dir):
        outdir = Path(temp_dir, "temp_out")
        parents = sys.maxsize
        with pytest.raises(
            IndexError, match=f"Parent index {parents} out of range"
        ):
            create_outdir(test_pdf, outdir, parents)


class TestRunProc:
    def test_successful_proc(self):
        proc = Popen("exit 0", shell=True)
        run_proc(proc, timeout=30)

    def test_timeout(self):
        proc = Popen("sleep 10", shell=True)
        with pytest.raises(TimeoutExpired):
            run_proc(proc, timeout=0)

    def test_critical_error(self):
        proc = Popen("exit 1", shell=True)
        with pytest.raises(ProcessError):
            run_proc(proc, timeout=30)

    def test_process_error(self):
        proc = Popen(">&2 echo error", shell=True, stderr=PIPE)
        with pytest.raises(ProcessError):
            run_proc(proc, timeout=30)
