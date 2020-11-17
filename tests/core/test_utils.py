# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
from subprocess import PIPE
from subprocess import Popen
from subprocess import TimeoutExpired

import pytest

from convertool.core.utils import run_proc
from convertool.exceptions import ProcessError

# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------


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
