from pathlib import Path

from acacore.siegfried import Siegfried

from convertool.converters import ConverterAudio
from convertool.converters.base import dummy_base_file

MIMETYPES: dict[str, list[str]] = {
    "mp3": ["audio/mpeg"],
    "wav": ["audio/wav", "audio/x-wav"],
    "flac": ["audio/flac"],
}


def test_audio(test_files: dict[str, Path], output_dir: Path, siegfried: Siegfried):
    for path in [f for n, f in test_files.items() if n.startswith("audio.")]:
        file = dummy_base_file(path, path.parent)
        converter = ConverterAudio(file)

        for output, mimetypes in MIMETYPES.items():
            output_files = converter.convert(output_dir, output)
            assert len(output_files) == 1
            assert siegfried.identify(output_files[0]).files[0].best_match().mime in mimetypes
