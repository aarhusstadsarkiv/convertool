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
            sf_match = siegfried.identify(output_files[0]).files[0].best_match()
            assert sf_match is not None
            assert sf_match.mime in mimetypes
            output_puid = converter.output_puid(output)
            assert output_puid is None or sf_match.id == converter.output_puid(output)
