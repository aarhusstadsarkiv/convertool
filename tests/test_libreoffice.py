import sys
import os
import platform
import pytest
from convertool.libreoffice import (
    find_libre,
    convert_files,
    LibreError,
    ConversionError,
)
from convertool.utils import get_files, WrongOSError


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


class TestConvertFiles:
    script_path = os.path.dirname(os.path.realpath(__file__))
    test_path = os.path.join(script_path, "test_data")
    valid_path = os.path.join(test_path, "data")
    out_path = os.path.join(test_path, "out")
    files = get_files(valid_path)

    def test_with_valid_input(self, caplog):
        convert_files(self.files, self.out_path)
        test_file = os.path.join(self.out_path, "test.pdf")
        log_msg = [record.message for record in caplog.records]

        # test.pdf is a file, and there should be no log message
        assert os.path.isfile(test_file)
        assert not log_msg
        # Clean up
        os.remove(test_file)

    def test_with_invalid_command(self):
        # This needs to be rewritten. Raises because ln(1)=0!!
        with pytest.raises(ConversionError):
            convert_files(self.files, self.out_path, libre="bogus")

    def test_with_invalid_file(self, caplog):
        convert_files(["bogus"], self.out_path)
        log_msg = [record.message for record in caplog.records]
        assert (
            "Conversion of bogus failed with error Error: source file"
            in log_msg[0]
        )

    def test_with_invalid_pname(self):
        with pytest.raises(ConversionError):
            convert_files(self.files, self.out_path, pname=sys.maxsize)

    def test_timeout(self, caplog):
        convert_files(self.files, self.out_path, timeout=0)
        log_msg = [record.message for record in caplog.records]
        assert f"Conversion of {self.files[0]}" in log_msg[0]
        assert f"timed out after 0 seconds" in log_msg[0]
