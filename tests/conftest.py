from functools import wraps
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
    for obj_name in converters.__all__:
        if (
            isinstance(obj := getattr(converters, obj_name), type)
            and issubclass(obj, converters.ConverterABC)
            and obj.process_timeout
        ):
            if obj.process_timeout and environ.get("PROCESS_TIMEOUT_MULTIPLIER", "").isdigit():
                obj.process_timeout *= int(environ["PROCESS_TIMEOUT_MULTIPLIER"])

            if environ.get("NO_CAPTURE_OUTPUT", "") == "true":
                original_init = obj.__init__

                @wraps(original_init)
                def _init(*args, **kwargs):
                    original_init(*args, **(kwargs | {"capture_output": False}))

                obj.__init__ = _init

            setattr(converters, obj_name, obj)


@pytest.fixture(scope="session")
def siegfried() -> Siegfried:
    return Siegfried(environ["SIEGFRIED_PATH"], "default.sig", environ["SIEGFRIED_HOME"])


@pytest.fixture(scope="session")
def avid_dir() -> Path:
    return Path(__file__).parent.joinpath("avid")


# noinspection DuplicatedCode
@pytest.fixture
def avid_dir_copy(avid_dir: Path) -> Path:
    copy_dir: Path = avid_dir.parent.joinpath(f"_{avid_dir.name}")
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
@pytest.fixture
def test_files_dir_copy(test_files_dir: Path) -> Path:
    copy_dir: Path = test_files_dir.parent.joinpath(f"_{test_files_dir.name}")
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
