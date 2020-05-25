from subprocess import PIPE, Popen, TimeoutExpired

import pytest
from convertool.exceptions import ProcessError, WrongOSError
from convertool.utils import check_system, get_files, run_proc


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
