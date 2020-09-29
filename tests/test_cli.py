import logging
import os
import sys
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from convertool.cli import cli


@pytest.fixture
def cli_run():
    return CliRunner()


@pytest.fixture(autouse=True)
def clean_up_files():
    script_path = os.path.dirname(os.path.realpath(__file__))
    test_path = os.path.join(script_path, "test_data")
    out_path = os.path.join(test_path, "out")
    try:
        os.mkdir(out_path)
    except Exception:
        pass
    yield
    logging.shutdown()
    for file in os.listdir(out_path):
        try:
            os.remove(os.path.join(out_path, file))
        except PermissionError:
            pass


class TestCli:
    script_path = os.path.dirname(os.path.realpath(__file__))
    test_path = os.path.join(script_path, "test_data")
    valid_path = os.path.join(test_path, "data")
    out_path = os.path.join(test_path, "out")

    def test_with_valid_input(self, cli_run):
        with cli_run.isolated_filesystem():
            args = [self.valid_path, self.out_path, "libre"]
            result = cli_run.invoke(cli, args)
            assert result.exit_code == 0

    def test_with_invalid_system(self, cli_run):
        wrong_sys = "Lamix"
        # Patch platform.system() call to return wrong_sys instead of
        # actual system information. This will make the CLI fail.
        with patch("platform.system", return_value=wrong_sys):
            with cli_run.isolated_filesystem():
                args = [self.valid_path, self.out_path, "libre"]
                result = cli_run.invoke(cli, args)
                assert result.exit_code != 0
                assert (
                    f"Expected to run on Windows or Linux, got {wrong_sys}"
                    in result.output
                )

    def test_with_invalid_files(self, cli_run):
        with cli_run.isolated_filesystem():
            args = ["bogus", self.out_path, "libre"]
            result = cli_run.invoke(cli, args)
            assert result.exit_code != 0
            assert "Error: Invalid value for 'FILES'" in result.output
            assert "Path 'bogus' does not exist." in result.output

    def test_with_invalid_outdir(self, cli_run):
        with cli_run.isolated_filesystem():
            args = [self.valid_path, "bogus", "libre"]
            result = cli_run.invoke(cli, args)
            assert result.exit_code != 0
            assert "Error: Invalid value for 'OUTDIR'" in result.output
            assert "Directory 'bogus' does not exist." in result.output

    def test_with_empty_filedir(self, cli_run):
        empty_test = os.path.join(self.test_path, "test_empty.txt")
        with cli_run.isolated_filesystem():
            args = [empty_test, self.out_path, "libre"]
            result = cli_run.invoke(cli, args)
            assert result.exit_code != 0
            assert f"{empty_test} is empty. Aborting" in result.output

    def test_with_invalid_parents(self, cli_run):
        with cli_run.isolated_filesystem():
            args = [
                f"--parents={sys.maxsize}",
                self.valid_path,
                self.out_path,
                "libre",
            ]
            result = cli_run.invoke(cli, args)
            assert result.exit_code != 0
            assert (
                f"Parent index {sys.maxsize} out of range for" in result.output
            )
