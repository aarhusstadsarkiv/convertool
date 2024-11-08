from pathlib import Path
from tempfile import TemporaryDirectory
from typing import ClassVar

from .base import ConverterABC


class ConverterVideo(ConverterABC):
    tool_names: ClassVar[list[str]] = ["video"]
    outputs: ClassVar[list[str]] = [
        "mpeg2",
        "h264",
        "h265",
    ]
    process_timeout: ClassVar[float] = 7200
    dependencies: ClassVar[list[str]] = ["ffmpeg"]

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path, mkdir=False)
        arguments: list[str] = []

        if output == "mpeg2":
            output = "mpg"
            arguments.extend(["-c:v", "mpeg2video", "-c:a", "mp3"])
        elif output == "h264":
            output = "mp4"
            arguments.extend(["-c:v", "libx264", "-c:a", "aac"])
        elif output == "h265":
            output = "mp4"
            arguments.extend(["-c:v", "libx265", "-c:a", "aac", "-vtag", "hvc1"])

        dest_file: Path = self.output_file(dest_dir, output)

        with TemporaryDirectory() as tmp_dir:
            tmp_dir = Path(tmp_dir)
            self.run_process(
                "ffmpeg",
                "-i",
                self.file.get_absolute_path(),
                "-nostdin",
                "-loglevel",
                "error",
                "-stats",
                *arguments,
                dest_file.name,
                cwd=tmp_dir,
            )
            dest_dir.mkdir(parents=True, exist_ok=True)
            tmp_dir.joinpath(dest_file.name).replace(dest_file)

        return [dest_file]
