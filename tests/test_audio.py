from pathlib import Path

from acacore.siegfried import Siegfried

from convertool.converters import ConverterAudio
from convertool.converters.base import dummy_base_file


def test_audio_to_mp3(test_files: dict[str, Path], output_dir: Path, siegfried: Siegfried):
    for path in [f for n, f in test_files.items() if n.startswith("audio.")]:
        file = dummy_base_file(path, path.parent)
        converter = ConverterAudio(file)

        output_files = converter.convert(output_dir, "mp3")
        assert len(output_files) == 1
        assert siegfried.identify(output_files[0]).files[0].best_match().mime == "audio/mpeg"


def test_audio_to_wav(test_files: dict[str, Path], output_dir: Path, siegfried: Siegfried):
    for path in [f for n, f in test_files.items() if n.startswith("audio.")]:
        file = dummy_base_file(path, path.parent)
        converter = ConverterAudio(file)

        output_files = converter.convert(output_dir, "wav")
        assert len(output_files) == 1
        assert siegfried.identify(output_files[0]).files[0].best_match().mime in ("audio/wav", "audio/x-wav")
