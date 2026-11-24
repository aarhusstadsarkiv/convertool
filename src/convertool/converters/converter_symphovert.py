from functools import lru_cache
from pathlib import Path
from shutil import which
from subprocess import run as run_process
from time import sleep
from typing import ClassVar

import pyperclip

from convertool.util import TempDir

from .base import ConverterABC
from .exceptions import ConvertError
from .exceptions import MissingDependency

# noinspection PyBroadException
try:
    import pyautogui
# Bare except because there are other errors than ImportError that can be raised when importing pyautogui depending on the system
except:  # noqa: E722
    pyautogui = None


def copypaste(string: str):
    pyperclip.copy(string)
    pyautogui.hotkey("ctrl", "v")
    pyautogui.press("enter")


class SymphovertConverter(ConverterABC):
    name: ClassVar[str] = "symphovert"
    platforms: ClassVar[list[str]] = ["win32"]
    dependencies: ClassVar[dict[str, list[str]]] = {"symphony": ["symphony"]}
    outputs: ClassVar[list[str]] = ["odt", "ods", "odp"]

    @classmethod
    def output_name(cls, output: str) -> str:
        if output == "odt":
            return "document"
        if output == "ods":
            return "spreadsheet"
        if output == "odp":
            return "presentation"
        return output

    def output_extension(self, output: str) -> str:
        if output == "odt":
            return ".odt"
        if output == "ods":
            return ".ods"
        if output == "odp":
            return ".odp"
        return f".{output}"

    @classmethod
    @lru_cache
    def test_dependencies(cls):
        if pyautogui is None:
            raise MissingDependency(["pyautogui"])
        if not (taskkill_which := which("taskkill")):
            raise MissingDependency(["taskkill"])
        cls.dependencies["taskkill"] = [taskkill_which]
        super().test_dependencies()

    def output_filename(self, output: str, *, append: bool = False) -> str:
        if append:
            return self.file.name + f".{output}"
        return self.file.relative_path.with_suffix(f".{output}").name

    def convert_file(self, src: Path, dst: Path):
        if pyautogui is None:
            raise MissingDependency(["pyautogui"])

        self.run_process(self.dependencies["symphony"][0])
        sleep(2)

        self.run_process("Get-Process", "-Name", "symphony")

        pyautogui.PAUSE = 1
        pyautogui.FAILSAFE = False

        pyautogui.hotkey("ctrl", "o", interval=0.5)
        sleep(1)
        copypaste(str(src))
        sleep(0.5)

        # Symphony opens an extra menu when ctrl+o is used, Escape closes it
        pyautogui.press("escape")
        sleep(2)

        dst.parent.mkdir(parents=True, exist_ok=True)

        # Save the file
        pyautogui.hotkey("ctrl", "shift", "s", interval=0.1)
        copypaste(str(dst))
        sleep(2)

        # Kill Symphony
        run_process(
            [self.dependencies["taskkill"][0], "/f", "/im", Path(self.dependencies["symphony"][0]).name],
            shell=True,
            capture_output=True,
            check=False,
        )

        sleep(2)

    def converter(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        self.test_output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = dest_dir.joinpath(self.output_filename(output))

        if dest_file.is_file():
            return [dest_file]

        with TempDir(output_dir) as tmp_dir:
            temp_file: Path = tmp_dir.joinpath(dest_file.name)
            self.convert_file(self.file.get_absolute_path(), temp_file)
            if temp_file.is_file():
                return [temp_file.replace(dest_file)]

        raise ConvertError(self.file, "Output file was not saved")
