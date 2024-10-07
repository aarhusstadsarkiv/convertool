from pathlib import Path

from acacore.models.file import File
from acacore.siegfried import Siegfried

from convertool.converters import ConverterVideo


def test_video_to_mpeg2(test_files: dict[str, Path], output_dir: Path, siegfried: Siegfried):
    for path in [f for n, f in test_files.items() if n.startswith("video.")]:
        file = File.from_file(path, root=path.parent)
        converter = ConverterVideo(file)

        output_files = converter.convert(output_dir, "mpeg2")
        assert len(output_files) == 1
        assert output_files[0].suffix == ".mpg"
        assert siegfried.identify(output_files[0]).files[0].best_match().mime == "video/mpeg"


def test_video_to_h264(test_files: dict[str, Path], output_dir: Path, siegfried: Siegfried):
    for path in [f for n, f in test_files.items() if n.startswith("video.")]:
        file = File.from_file(path, root=path.parent)
        converter = ConverterVideo(file)

        output_files = converter.convert(output_dir, "h264")
        assert len(output_files) == 1
        assert output_files[0].suffix == ".mp4"
        assert siegfried.identify(output_files[0]).files[0].best_match().mime in "application/mp4"


def test_video_to_h265(test_files: dict[str, Path], output_dir: Path, siegfried: Siegfried):
    for path in [f for n, f in test_files.items() if n.startswith("video.")]:
        file = File.from_file(path, root=path.parent)
        converter = ConverterVideo(file)

        output_files = converter.convert(output_dir, "h265")
        assert len(output_files) == 1
        assert output_files[0].suffix == ".mp4"
        assert siegfried.identify(output_files[0]).files[0].best_match().mime in "application/mp4"
