import sys
import os
import pytest
from click.testing import CliRunner
from convertool.cli import cli


@pytest.fixture
def cli_run():
    return CliRunner()


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

    def test_with_invalid_files(self, cli_run):
        with cli_run.isolated_filesystem():
            args = ["bogus", self.out_path, "libre"]
            result = cli_run.invoke(cli, args)
            assert result.exit_code != 0
            assert 'Error: Invalid value for "FILES"' in result.output
            assert 'Path "bogus" does not exist.' in result.output

    def test_with_invalid_outdir(self, cli_run):
        with cli_run.isolated_filesystem():
            args = [self.valid_path, "bogus", "libre"]
            result = cli_run.invoke(cli, args)
            assert result.exit_code != 0
            assert 'Error: Invalid value for "OUTDIR"' in result.output
            assert 'Directory "bogus" does not exist.' in result.output

    def test_with_empty_filedir(self, cli_run):
        empty_test = os.path.join(self.test_path, "test_empty.txt")
        with cli_run.isolated_filesystem():
            args = [empty_test, self.out_path, "libre"]
            result = cli_run.invoke(cli, args)
            assert result.exit_code != 0
            assert f"{empty_test} is empty. Aborting" in result.output

    def test_with_invalid_pname(self, cli_run):
        with cli_run.isolated_filesystem():
            args = [
                f"--pname={sys.maxsize}",
                self.valid_path,
                self.out_path,
                "libre",
            ]
            result = cli_run.invoke(cli, args)
            assert result.exit_code != 0
            assert (
                f"Error: Parent index {sys.maxsize} out of range for"
                in result.output
            )
