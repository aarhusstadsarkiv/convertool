# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
# from typing import Any
# from typing import Dict
from typing import List
from uuid import UUID

import sqlalchemy as sql
from acamodels import ArchiveFile
from databases import Database
from pydantic import parse_obj_as
from pydantic import ValidationError

from convertool.exceptions import FileParseError

# -----------------------------------------------------------------------------
# Database class
# -----------------------------------------------------------------------------


class FileDB(Database):
    """File database"""

    sql_meta = sql.MetaData()
    converted_files = sql.Table(
        "_ConvertedFiles",
        sql_meta,
        sql.Column(
            "file_id",
            sql.Integer,
            sql.ForeignKey("Files.id"),
            nullable=False,
        ),
        sql.Column("uuid", sql.Unicode, nullable=False),
        extend_existing=True,
    )

    def __init__(self, url: str) -> None:
        super().__init__(url)
        self.engine = sql.create_engine(
            url, connect_args={"check_same_thread": False}
        )

        # Table reflection
        self.sql_meta.reflect(bind=self.engine)
        self.files = self.sql_meta.tables["Files"]
        self.converted_files.create(self.engine, checkfirst=True)

    async def get_files(self) -> List[ArchiveFile]:
        query = self.files.select()
        rows = await self.fetch_all(query)
        try:
            files = parse_obj_as(List[ArchiveFile], rows)
        except ValidationError:
            raise FileParseError("Failed to parse files as ArchiveFiles.")
        else:
            return files

    async def update_status(self, uuid: UUID) -> None:
        async with self.transaction():
            get_file_id = self.files.select().where(
                self.files.c.uuid == str(uuid)
            )
            file_id = await self.fetch_val(get_file_id, column="id")
            exists = await self.check_status(uuid)
            if not exists:
                insert_file = self.converted_files.insert()
                insert_values = {"file_id": file_id, "uuid": str(uuid)}
                await self.execute(insert_file, insert_values)
            else:
                return

    async def check_status(self, uuid: UUID) -> bool:
        conv_files = self.converted_files
        select_uuid = conv_files.select().where(conv_files.c.uuid == str(uuid))
        check = await self.fetch_one(select_uuid)
        return bool(check)
