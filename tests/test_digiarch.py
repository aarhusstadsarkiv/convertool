from pathlib import Path

from convertool.cli import app


def test_digiarch(test_files_dir: Path, output_dir: Path):
    app.main(["digiarch", str(test_files_dir), str(output_dir)], standalone_mode=False)
