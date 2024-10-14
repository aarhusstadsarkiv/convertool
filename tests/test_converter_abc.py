from pathlib import Path
from typing import ClassVar

import pytest

from convertool.converters import ConverterABC
from convertool.converters.exceptions import MissingDependency
from convertool.converters.exceptions import UnsupportedPlatform


def test_platforms():
    class Converter(ConverterABC):
        tool_names: ClassVar[list[str]] = ["tool"]
        outputs: ClassVar[list[str]] = ["out"]
        platforms: ClassVar[list[str]] = ["-invalid platform"]

        def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
            return []

    with pytest.raises(UnsupportedPlatform, match=Converter.platforms[0]) as platform_exception:
        Converter.test_platforms()


def test_dependencies():
    class Converter(ConverterABC):
        tool_names: ClassVar[list[str]] = ["tool"]
        outputs: ClassVar[list[str]] = ["out"]
        dependencies: ClassVar[list[str]] = ["-invalid dependency"]

        def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
            return []

    with pytest.raises(MissingDependency, match=Converter.dependencies[0]) as platform_exception:
        Converter.test_dependencies()
