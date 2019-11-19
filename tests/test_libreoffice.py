import os
import platform
import pytest
from click import ClickException
from convertool.libreoffice import find_libre, convert_files
from convertool.utils import get_files


class TestFindLibre:
    def test_with_valid_system(self):
        # Result is populated if all goes well
        result = find_libre(platform.system())
        assert result

    def test_with_invalid_system(self):
        with pytest.raises(ClickException):
            find_libre("not an os")

    def test_wrong_cmd(self):
        curr_system = platform.system()
        if curr_system != "Windows":
            # The windows command will fail
            with pytest.raises(ClickException):
                find_libre("Windows")
        elif curr_system != "Linux":
            # The Linux command will fail
            with pytest.raises(ClickException):
                find_libre("Linux")


class TestConvertFiles:
    system = platform.system()
    script_path = os.path.dirname(os.path.realpath(__file__))
    test_path = os.path.join(script_path, "test_data")
    valid_path = os.path.join(test_path, "data")
    out_path = os.path.join(test_path, "out")
    files = get_files(valid_path)

    def test_with_valid_input(self):
        convert_files(self.system, self.files, self.out_path)
        test_file = os.path.join(self.out_path, "test.pdf")
        assert os.path.isfile(test_file)
        # Clean up
        os.remove(test_file)

    def test_with_invalid_outdir(self):
        # Turns out LibreOffice doesn't care!
        pass

    def test_with_invalid_file(self):
        convert_files(self.system, ["bogus"], self.out_path)
        with open(os.path.join(self.out_path, "_convertool_log.txt")) as file:
            lines = file.readlines()
            expected_msg = "Conversion of bogus failed with error: "
            expected_msg += "Error: source file could not be loaded\n"
            assert expected_msg in lines
        # Clean up
        os.remove(os.path.join(self.out_path, "_convertool_log.txt"))
