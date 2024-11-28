from pathlib import Path

from acacore.database import FilesDB
from acacore.utils.functions import rm_tree

from convertool.cli import app
from convertool.util import AVID


# noinspection DuplicatedCode
def test_digiarch_original_master(avid_dir_copy: Path):
    avid = AVID(avid_dir_copy)

    with FilesDB(avid.database_path) as db:
        db.master_files.delete("uuid is not null")
        db.access_files.delete("uuid is not null")
        db.statutory_files.delete("uuid is not null")
        db.log.delete("operation like 'convertool.digiarch%'")
        # noinspection SqlWithoutWhere
        db.execute(f"update {db.original_files.name} set processed = false")
        db.commit()
        rm_tree(avid.dirs.master_documents)
        rm_tree(avid.dirs.access_documents)
        rm_tree(avid.dirs.documents)

    app.main(["digiarch", str(avid.path), "original:master"], standalone_mode=False)

    with FilesDB(avid.database_path) as db:
        for file in db.original_files.select():
            output_files = db.master_files.select({"original_uuid": str(file.uuid)}).fetchall()
            event = db.log.select(
                "file_uuid = ? and operation = 'convertool.digiarch:converted'",
                [str(file.uuid)],
            ).fetchone()
            assert event is None or isinstance(event.data, dict)
            if event and not event.data["files"]:
                assert not output_files
                assert file.processed
            elif event:
                assert len(output_files) == event.data["files"]
                assert all(f.get_absolute_path(avid.path).is_file() for f in output_files)
                assert file.processed
            else:
                assert not output_files
                assert not file.processed


# noinspection DuplicatedCode
def test_digiarch_master_access(avid_dir_copy: Path):
    avid = AVID(avid_dir_copy)

    with FilesDB(avid.database_path) as db:
        db.access_files.delete("uuid is not null")
        db.statutory_files.delete("uuid is not null")
        # noinspection SqlWithoutWhere
        db.execute(f"update {db.master_files.name} set processed = false")
        db.commit()
        rm_tree(avid.dirs.access_documents)
        rm_tree(avid.dirs.documents)

    app.main(["digiarch", str(avid.path), "master:access"], standalone_mode=False)

    with FilesDB(avid.database_path) as db:
        for file in db.master_files.select():
            output_files = db.access_files.select({"original_uuid": str(file.uuid)}).fetchall()
            event = db.log.select(
                "file_uuid = ? and operation = 'convertool.digiarch:converted'",
                [str(file.uuid)],
            ).fetchone()
            assert event is None or isinstance(event.data, dict)
            if event and not event.data["files"]:
                assert not output_files
                assert file.processed
            elif event:
                assert len(output_files) == event.data["files"]
                assert all(f.get_absolute_path(avid.path).is_file() for f in output_files)
                assert file.processed
            else:
                assert not output_files
                assert not file.processed


# noinspection DuplicatedCode
def test_digiarch_master_statutory(avid_dir_copy: Path):
    avid = AVID(avid_dir_copy)

    with FilesDB(avid.database_path) as db:
        db.access_files.delete("uuid is not null")
        db.statutory_files.delete("uuid is not null")
        # noinspection SqlWithoutWhere
        db.execute(f"update {db.master_files.name} set processed = false")
        db.commit()
        rm_tree(avid.dirs.access_documents)
        rm_tree(avid.dirs.documents)

    app.main(["digiarch", str(avid.path), "master:statutory"], standalone_mode=False)

    with FilesDB(avid.database_path) as db:
        for file in db.master_files.select():
            output_files = db.statutory_files.select({"original_uuid": str(file.uuid)}).fetchall()
            event = db.log.select(
                "file_uuid = ? and operation = 'convertool.digiarch:converted'",
                [str(file.uuid)],
            ).fetchone()
            assert event is None or isinstance(event.data, dict)
            if event and not event.data["files"]:
                assert not output_files
                assert file.processed
            elif event:
                assert len(output_files) == event.data["files"]
                assert all(f.get_absolute_path(avid.path).is_file() for f in output_files)
                assert file.processed
            else:
                assert not output_files
                assert not file.processed
