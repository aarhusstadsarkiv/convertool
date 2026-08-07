from pathlib import Path
from typing import ClassVar

from convertool.util import TempDir

from .base import ConverterABC


class AudioConverter(ConverterABC):
    name: ClassVar[str] = "audio"
    outputs: ClassVar[list[str]] = ["mp3", "wav", "flac"]
    process_timeout: ClassVar[float] = 1800
    dependencies: ClassVar[dict[str, list[str]]] = {"ffmpeg": ["ffmpeg"]}

    @classmethod
    def output_name(cls, output: str) -> str:
        return "audio"

    def output_extension(self, output: str) -> str:
        if output == "mp3":
            return ".mp3"
        if output == "wav":
            return ".wav"
        if output == "flac":
            return ".flac"
        return f".{output}"

    def output_puid(self, output: str) -> str | None:
        if output == "mp3":
            return "fmt/134"
        if output == "wav":
            return "fmt/141"
        if output == "flac":
            return "fmt/279"
        return None

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        self.test_output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = dest_dir.joinpath(self.output_file(output))
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
