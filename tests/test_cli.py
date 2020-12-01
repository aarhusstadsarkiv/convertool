# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import logging
import shutil

import pytest
from click.testing import CliRunner

import convertool.database as c_db
from convertool import core
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
    def test_with_valid_input(self, cli_run, test_data, test_out):
        test_db = test_data / "files.db"
        args = [str(test_db), str(test_out), "main"]
        result = cli_run.invoke(cli, args)
        assert result.exit_code == 0

    def test_with_invalid_files(self, cli_run, test_out):
        with cli_run.isolated_filesystem():
            args = ["bogus", str(test_out), "main"]
            result = cli_run.invoke(cli, args)
            assert result.exit_code != 0
            assert "Error: Invalid value for 'FILES'" in result.output
            assert "Path 'bogus' does not exist." in result.output

    def test_with_invalid_outdir(self, cli_run, test_files):
        with cli_run.isolated_filesystem():
            args = [str(test_files), "bogus", "main"]
            result = cli_run.invoke(cli, args)
            assert result.exit_code != 0
            assert "Error: Invalid value for 'OUTDIR'" in result.output
            assert "Directory 'bogus' does not exist." in result.output

    def test_exceptions(self, cli_run, test_data, test_out, monkeypatch):
        test_db = test_data / "files.db"
        args = [str(test_db), str(test_out), "main"]

        # Monkeypatch defs
        def init_except(*args):
            raise Exception("Init error")

        async def empty_files(*args):
            return []

        def convert_error(*args):
            raise ConversionError("Conversion error.")

        # Fail to load db
        monkeypatch.setattr(c_db.FileDB, "__init__", init_except)
        result = cli_run.invoke(cli, args)
        assert (
            result.output.strip()
            == f"Error: Failed to load {test_db} as a database."
        )
        assert result.exit_code == 1
        monkeypatch.undo()

        # No files
        monkeypatch.setattr(c_db.FileDB, "get_files", empty_files)
        result = cli_run.invoke(cli, args)
        assert "Error: Database is empty. Aborting." in result.output.strip()
        assert result.exit_code == 1
        monkeypatch.undo()

        # Conversion error
        monkeypatch.setattr(core.FileConv, "convert", convert_error)
        result = cli_run.invoke(cli, args)
        assert "Error: Conversion error." in result.output.strip()
        assert result.exit_code == 1
        monkeypatch.undo()
