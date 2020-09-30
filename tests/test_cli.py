# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import logging
import platform
import shutil
import sys

import pytest
from click.testing import CliRunner

import convertool
from convertool.cli import cli
from convertool.exceptions import ConversionError

# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------


@pytest.fixture
def cli_run():
    return CliRunner()


@pytest.fixture(autouse=True)
def clean_up_files(test_out):
    test_out.mkdir(exist_ok=True)
    yield
    logging.shutdown()
    shutil.rmtree(test_out, ignore_errors=True)


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------


class TestCli:
    def test_with_valid_input(self, cli_run, test_files, test_out):
        with cli_run.isolated_filesystem():
            args = [str(test_files), str(test_out), "libre"]
            result = cli_run.invoke(cli, args)
            assert result.exit_code == 0

    def test_context(self, cli_run, test_files, test_out, monkeypatch):
        with cli_run.isolated_filesystem():
            args = [str(test_files), str(test_out), "context"]
            result = cli_run.invoke(cli, args)
            assert result.exit_code == 0

            # Raise conversion error
            def raise_conv_error(*args):
                raise ConversionError("test")

            monkeypatch.setattr(
                convertool.cli, "convert_files", raise_conv_error
            )
            result = cli_run.invoke(cli, args)
            assert result.exit_code != 0
            assert "Error: test" in result.output

    def test_with_invalid_system(
        self, cli_run, test_files, test_out, monkeypatch
    ):
        # Patch return of platform.system
        wrong_sys = "Lamix"
        monkeypatch.setattr(platform, "system", lambda: wrong_sys)
        with cli_run.isolated_filesystem():
            args = [str(test_files), str(test_out), "libre"]
            result = cli_run.invoke(cli, args)
            assert result.exit_code != 0
            assert (
                f"Expected to run on Windows or Linux, got {wrong_sys}"
                in result.output
            )

    def test_with_invalid_files(self, cli_run, test_out):
        with cli_run.isolated_filesystem():
            args = ["bogus", str(test_out), "libre"]
            result = cli_run.invoke(cli, args)
            assert result.exit_code != 0
            assert "Error: Invalid value for 'FILES'" in result.output
            assert "Path 'bogus' does not exist." in result.output

    def test_with_invalid_outdir(self, cli_run, test_files):
        with cli_run.isolated_filesystem():
            args = [str(test_files), "bogus", "libre"]
            result = cli_run.invoke(cli, args)
            assert result.exit_code != 0
            assert "Error: Invalid value for 'OUTDIR'" in result.output
            assert "Directory 'bogus' does not exist." in result.output

    def test_with_empty_filedir(self, cli_run, test_data, test_out):
        empty_test = test_data / "test_empty.txt"
        empty_test.touch()
        with cli_run.isolated_filesystem():
            args = [str(empty_test), str(test_out), "libre"]
            result = cli_run.invoke(cli, args)
            assert result.exit_code != 0
            assert f"{empty_test} is empty. Aborting" in result.output
        empty_test.unlink()

    def test_with_invalid_parents(self, cli_run, test_files, test_out):
        with cli_run.isolated_filesystem():
            args = [
                f"--parents={sys.maxsize}",
                str(test_files),
                str(test_out),
                "libre",
            ]
            result = cli_run.invoke(cli, args)
            assert result.exit_code != 0
            assert (
                f"Parent index {sys.maxsize} out of range for" in result.output
            )
