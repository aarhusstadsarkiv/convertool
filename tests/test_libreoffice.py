import os
import platform
import pytest
from convertool.libreoffice import find_libre, libre_convert
from convertool.utils import get_files
from convertool.exceptions import WrongOSError, LibreError


@pytest.fixture
def file_handler():
    script_path = os.path.dirname(os.path.realpath(__file__))
    test_path = os.path.join(script_path, "test_data")
    valid_path = os.path.join(test_path, "data")
    out_path = os.path.join(test_path, "out")
    file = get_files(valid_path)[0]
    yield out_path, file
    for file in os.listdir(out_path):
        os.remove(os.path.join(out_path, file))


class TestFindLibre:
    def test_with_valid_system(self):
        # Result is populated if all goes well
        result = find_libre(platform.system())
        assert result

    def test_with_invalid_system(self):
        with pytest.raises(WrongOSError):
            find_libre("not an os")

    def test_wrong_cmd(self):
        curr_system = platform.system()
        if curr_system == "Linux":
            # The Windows command will fail
            with pytest.raises(LibreError):
                find_libre("Windows")
        elif curr_system == "Windows":
            # The Linux command will fail
            with pytest.raises(LibreError):
                find_libre("Linux")


class TestLibreConvert:
    def test_with_valid_input(self, file_handler):
        out, file = file_handler
        libre_convert(file, out, "pdf")
        test_file = os.path.join(out, "test.pdf")
        assert os.path.isfile(test_file)

    def test_with_invalid_command(self, file_handler):
        out, file = file_handler
        with pytest.raises(LibreError):
            libre_convert(file, out, "pdf", cmd="bogus")

    def test_with_invalid_file(self, file_handler):
        out, file = file_handler
        with pytest.raises(LibreError):
            libre_convert("bogus", out, "pdf")

    def test_timeout(self, file_handler):
        out, file = file_handler
        with pytest.raises(LibreError):
            libre_convert(file, out, "pdf", timeout=0)
