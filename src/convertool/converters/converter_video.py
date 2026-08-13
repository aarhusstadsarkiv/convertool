from pathlib import Path
from typing import ClassVar

from convertool.util import TempDir

from .base import ConverterABC


class VideoConverter(ConverterABC):
    name: ClassVar[str] = "video"
    outputs: ClassVar[list[str]] = [
        "mpeg2",
        "h264",
        "h264-mpg",
        "h265",
    ]
    process_timeout: ClassVar[float] = 7200
    dependencies: ClassVar[dict[str, list[str]]] = {"ffmpeg": ["ffmpeg"]}

    @classmethod
    def output_name(cls, output: str) -> str:
        return "video"

    def output_extension(self, output: str) -> str:
        if output == "mpeg2":
            return ".mpg"
        if output == "h264":
            return ".mp4"
        if output == "h264-mpg":
            return ".mpg"
        if output == "h265":
            return ".mp4"
        return f".{output}"

    def output_puid(self, output: str) -> str | None:
        if output == "mpeg2":
            return "x-fmt/386"
        if output == "h264":
            return "fmt/199"
        if output == "h264-mpg":
            return "fmt/199"
        if output == "h265":
            return "fmt/199"
        return None

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        self.test_output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = dest_dir.joinpath(self.output_filename(output))
        temp_extension: str | None = None
        arguments: list[str] = []

        if output == "mpeg2":
            arguments.extend(["-c:v", "mpeg2video", "-c:a", "mp3"])
        elif output == "h264":
            arguments.extend(["-c:v", "libx264", "-c:a", "aac"])
        elif output == "h264-mpg":
            temp_extension = "mp4"
            arguments.extend(["-c:v", "libx264", "-c:a", "aac"])
        elif output == "h265":
            arguments.extend(["-c:v", "libx265", "-c:a", "aac", "-vtag", "hvc1"])

        with TempDir(output_dir) as tmp_dir:
            tmp_file = tmp_dir.joinpath(dest_file.with_suffix(temp_extension or dest_file.suffix).name)

            self.run_process(
                self.dependencies["ffmpeg"][0],
                "-i",
                self.file.get_absolute_path(),
                "-nostdin",
                "-loglevel",
                "error",
                "-stats",
                *arguments,
                tmp_file.name,
                cwd=tmp_dir,
            )

            dest_dir.mkdir(parents=True, exist_ok=True)
            tmp_file.replace(dest_file)

        return [dest_file]
