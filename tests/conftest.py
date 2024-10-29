from os import environ
from pathlib import Path
from shutil import copy2

import pytest
from acacore.siegfried import Siegfried
from acacore.utils.functions import find_files
from acacore.utils.functions import rm_tree


@pytest.fixture(scope="session")
def siegfried() -> Siegfried:
    return Siegfried(environ["SIEGFRIED_PATH"], "default.sig", environ["SIEGFRIED_HOME"])


@pytest.fixture(scope="session")
def test_files_dir() -> Path:
    return Path(__file__).parent.joinpath("files")


@pytest.fixture(scope="session")
def test_files_dir_copy(test_files_dir: Path) -> Path:
    copy_dir: Path = test_files_dir.parent.joinpath("_files")
    rm_tree(copy_dir)
    copy_dir.mkdir(parents=True, exist_ok=True)
    for file in find_files(test_files_dir):
        copy_dir.joinpath(file.parent.relative_to(test_files_dir)).mkdir(parents=True, exist_ok=True)
        copy2(file, copy_dir.joinpath(file.relative_to(test_files_dir)))
    return copy_dir


@pytest.fixture(scope="session")
def test_files(test_files_dir: Path) -> dict[str, Path]:
    return {f.name: f for f in test_files_dir.iterdir() if f.is_file()}


@pytest.fixture(scope="session")
def reference_files() -> dict[str, Path]:
    return {f.name: f for f in Path(__file__).parent.joinpath("reference").iterdir() if f.is_file()}


@pytest.fixture
def output_dir() -> Path:
    rm_tree(path := Path(__file__).parent.joinpath("output"))
    return path
