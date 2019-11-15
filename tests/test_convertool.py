import os
import pytest
from click.testing import CliRunner
from convertool.convertool import cli


@pytest.fixture
def cli_run():
    return CliRunner()


class TestCli:
    def test_with_valid_input(self, cli_run):
        script_path = os.path.dirname(os.path.realpath(__file__))
        print(script_path)
        assert False
