import pytest
from subprocess import Popen, TimeoutExpired, PIPE
from convertool.utils import get_files, check_system, run_proc
from convertool.exceptions import WrongOSError, ProcessError


class TestGetFiles:
    def test_with_file(self, list_file):
        result = get_files(list_file)
        assert len(result) == 2

    def test_with_dir(self, data_dir):
        result = get_files(data_dir)
        assert len(result) == 2

    def test_with_nothing(self):
        result = get_files("nothing_here")
        assert len(result) == 0


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


class TestRunProc:
    def test_successful_proc(self):
        proc = Popen(f"exit 0", shell=True)
        run_proc(proc, timeout=30)

    def test_timeout(self):
        proc = Popen(f"exit 0", shell=True)
        with pytest.raises(TimeoutExpired):
            run_proc(proc, timeout=0)

    def test_critical_error(self):
        proc = Popen(f"exit 1", shell=True)
        with pytest.raises(ProcessError):
            run_proc(proc, timeout=30)

    def test_process_error(self):
        proc = Popen(f">&2 echo error", shell=True, stderr=PIPE)
        with pytest.raises(ProcessError):
            run_proc(proc, timeout=30)
