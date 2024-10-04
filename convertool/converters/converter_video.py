from pathlib import Path
from typing import ClassVar

from acacore.utils.functions import rm_tree

from .base import ConverterABC


class ConverterVideo(ConverterABC):
    tool_names: ClassVar[list[str]] = ["video"]
    outputs: ClassVar[list[str]] = [
        "mpeg2",
        "h264",
        "h265",
    ]
    process_timeout: ClassVar[float] = 7200

    def convert(
        self,
        output_dir: Path,
        output: str,
        *,
        keep_relative_path: bool = True,
    ) -> list[Path]:
        output = self.output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path)
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

        dest_dir_tmp: Path = dest_dir / f"_{dest_file.name}.ffmpeg"
        while dest_dir_tmp.exists() and not dest_dir_tmp.is_dir():
            dest_dir_tmp = dest_dir_tmp.with_name("_" + dest_dir_tmp.name)

        rm_tree(dest_dir_tmp)
        dest_dir_tmp.mkdir(parents=True, exist_ok=True)

        try:
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
                cwd=dest_dir_tmp,
            )
            dest_dir_tmp.joinpath(dest_file.name).replace(dest_file)
        finally:
            rm_tree(dest_dir_tmp)

        return [dest_file]
