from os import environ
from pathlib import Path
from shutil import copy2

import pytest
from acacore.siegfried import Siegfried
from acacore.utils.functions import find_files
from acacore.utils.functions import rm_tree

from convertool import converters


@pytest.fixture(scope="session", autouse=True)
def on_test_start():
    if not environ.get("PROCESS_TIMEOUT_MULTIPLIER", "").isdigit():
        return
    for obj_name in converters.__all__:
        if (
            isinstance(obj := getattr(converters, obj_name), type)
            and issubclass(obj, converters.ConverterABC)
            and obj.process_timeout
        ):
            obj.process_timeout *= int(environ["PROCESS_TIMEOUT_MULTIPLIER"])
            setattr(converters, obj_name, obj)


@pytest.fixture(scope="session")
def siegfried() -> Siegfried:
    return Siegfried(environ["SIEGFRIED_PATH"], "default.sig", environ["SIEGFRIED_HOME"])


@pytest.fixture(scope="session")
def avid_dir() -> Path:
    return Path(__file__).parent.joinpath("avid")


# noinspection DuplicatedCode
@pytest.fixture(scope="session")
def avid_dir_copy(avid_dir: Path) -> Path:
    copy_dir: Path = avid_dir.parent.joinpath("_avid")
    rm_tree(copy_dir)
    copy_dir.mkdir(parents=True, exist_ok=True)
    for file in find_files(avid_dir):
        copy_dir.joinpath(file.parent.relative_to(avid_dir)).mkdir(parents=True, exist_ok=True)
        copy2(file, copy_dir.joinpath(file.relative_to(avid_dir)))
    return copy_dir


@pytest.fixture(scope="session")
def test_files_dir(avid_dir: Path) -> Path:
    return avid_dir.joinpath("OriginalDocuments")


# noinspection DuplicatedCode
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
    path.mkdir(parents=True, exist_ok=True)
    return path
