from pathlib import Path
from subprocess import run as run_process
from time import sleep
from typing import ClassVar

import pyperclip

from convertool.util import TempDir

from .base import ConverterABC
from .exceptions import ConvertError
from .exceptions import MissingDependency

try:
    import pyautogui
except (ImportError, KeyError):
    pyautogui = None


def copypaste(string: str):
    pyperclip.copy(string)
    pyautogui.hotkey("ctrl", "v")
    pyautogui.press("enter")


class ConverterSymphovert(ConverterABC):
    tool_names: ClassVar[list[str]] = ["symphovert"]
    platforms: ClassVar[list[str]] = ["win32"]
    dependencies: ClassVar[dict[str, list[str]]] = {"symphony": ["symphony"]}
    outputs: ClassVar[list[str]] = ["odt", "ods", "odp"]

    @classmethod
    def test_dependencies(cls):
        if pyautogui is None:
            raise MissingDependency(["pyautogui"])
        super().test_dependencies()

    def output_file(self, output_dir: Path, output: str, *, append: bool = False) -> Path:
        if append:
            return output_dir / (self.file.name + f".{output}")
        return output_dir / self.file.relative_path.with_suffix(f".{output}").name

    def convert_file(self, src: Path, dst: Path):
        if pyautogui is None:
            raise MissingDependency(["pyautogui"])

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
            ["taskkill", "/f", "/im", self.dependencies["symphony"][0] + "*"],
            shell=True,
            capture_output=True,
            check=False,
        )

        sleep(0.5)

    def run_symphony(self):
        self.run_process(self.dependencies["symphony"][0])

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = self.output_file(dest_dir, output)

        if dest_file.is_file():
            return [dest_file]

        self.run_symphony()
        sleep(2)

        with TempDir(output_dir) as tmp_dir:
            temp_file: Path = tmp_dir.joinpath(dest_file.name)
            self.convert_file(self.file.get_absolute_path(), temp_file)
            if temp_file.is_file():
                return [temp_file.replace(dest_file)]

        raise ConvertError(self.file, "Output file was not saved")
