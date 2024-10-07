from os import environ
from pathlib import Path

import pytest
from acacore.siegfried import Siegfried
from acacore.utils.functions import rm_tree


@pytest.fixture(scope="session")
def siegfried() -> Siegfried:
    return Siegfried(environ["SIEGFRIED_PATH"], "default.sig", environ["SIEGFRIED_HOME"])


@pytest.fixture(scope="session")
def test_files() -> dict[str, Path]:
    return {f.name: f for f in Path(__file__).parent.joinpath("files").iterdir() if f.is_file()}


@pytest.fixture(scope="session")
def reference_files() -> dict[str, Path]:
    return {f.name: f for f in Path(__file__).parent.joinpath("reference").iterdir() if f.is_file()}


@pytest.fixture(scope="function")
def output_dir() -> Path:
    rm_tree(path := Path(__file__).parent.joinpath("output"))
    return path
