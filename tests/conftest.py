"""Shared testing fixtures.

"""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import pytest
import os

# -----------------------------------------------------------------------------
# Function Definitions
# -----------------------------------------------------------------------------


@pytest.fixture
def temp_dir(tmpdir_factory):
    temp_dir: str = tmpdir_factory.mktemp("temp_dir")
    return temp_dir


@pytest.fixture
def data_dir(temp_dir):
    data_dir: str = temp_dir.mkdir("data")
    file1: str = os.path.join(data_dir, "file1.txt")
    file2: str = os.path.join(data_dir, "file2.txt")
    with open(file1, "w") as f1:
        f1.write("test1")
    with open(file2, "w") as f2:
        f2.write("test2")
    return data_dir


@pytest.fixture
def list_file(temp_dir):
    list_file: str = os.path.join(temp_dir, "data.txt")
    with open(list_file, "w") as file:
        file.writelines(["/dir/file1.txt\n", "/dir/file2.txt"])
    return list_file
