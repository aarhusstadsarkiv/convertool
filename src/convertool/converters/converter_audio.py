from pathlib import Path
from typing import ClassVar

from convertool.util import TempDir

from .base import ConverterABC


class ConverterAudio(ConverterABC):
    tool_names: ClassVar[list[str]] = ["audio"]
    outputs: ClassVar[list[str]] = [
        "mp3",
        "wav",
        "flac",
    ]
    process_timeout: ClassVar[float] = 1800
    dependencies: ClassVar[dict[str, list[str]]] = {"ffmpeg": ["ffmpeg"]}

    def output_puid(self, output: str) -> str | None:
        if output == "mp3":
            return "fmt/134"
        return None

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = self.output_file(dest_dir, output)
        arguments: list[str] = []

        if output == "mp3":
            arguments.extend(["-c:a", "mp3"])
        elif output == "wav":
            arguments.extend(["-c:a", "pcm_s16le"])

        with TempDir(output_dir) as tmp_dir:
            self.run_process(
                self.dependencies["ffmpeg"][0],
                "-i",
                self.file.get_absolute_path(),
                "-nostdin",
                "-loglevel",
                "error",
                "-stats",
                "-vn",
                *arguments,
                dest_file.name,
                cwd=tmp_dir,
            )
            dest_dir.mkdir(parents=True, exist_ok=True)
            tmp_dir.joinpath(dest_file.name).replace(dest_file)

        return [dest_file]
