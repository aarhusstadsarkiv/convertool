from pathlib import Path

from acacore.database import FileDB

from convertool.cli import app


def test_digiarch(test_files_dir_copy: Path, output_dir: Path):
    app.main(["digiarch", str(test_files_dir_copy), str(output_dir)], standalone_mode=False)

    with FileDB(test_files_dir_copy / "_metadata" / "files.db") as db:
        for file in db.files.select():
            if (
                event := db.history.select(
                    where="uuid = ? and operation = 'convertool.digiarch:converted'",
                    parameters=[str(file.uuid)],
                ).fetchone()
            ) and event.data == ["template", "temporary-file"]:
                assert not file.processed_names
            else:
                assert len(file.processed_names) >= 1
