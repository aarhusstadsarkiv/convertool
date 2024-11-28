from pathlib import Path

from acacore.models.file import BaseFile
from acacore.siegfried import Siegfried

from convertool.converters import ConverterAudio


def test_audio_to_mp3(test_files: dict[str, Path], output_dir: Path, siegfried: Siegfried):
    for path in [f for n, f in test_files.items() if n.startswith("audio.")]:
        file = BaseFile.from_file(path, root=path.parent)
        converter = ConverterAudio(file)

        output_files = converter.convert(output_dir, "mp3")
        assert len(output_files) == 1
        assert siegfried.identify(output_files[0]).files[0].best_match().mime == "audio/mpeg"


def test_audio_to_wav(test_files: dict[str, Path], output_dir: Path, siegfried: Siegfried):
    for path in [f for n, f in test_files.items() if n.startswith("audio.")]:
        file = BaseFile.from_file(path, root=path.parent)
        converter = ConverterAudio(file)

        output_files = converter.convert(output_dir, "wav")
        assert len(output_files) == 1
        assert siegfried.identify(output_files[0]).files[0].best_match().mime in ("audio/wav", "audio/x-wav")
