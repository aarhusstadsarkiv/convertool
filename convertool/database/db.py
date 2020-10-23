# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
from typing import List

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

    def __init__(self, url: str) -> None:
        super().__init__(url)
        self.engine = sql.create_engine(
            url, connect_args={"check_same_thread": False}
        )

        # Table reflection
        self.meta = sql.MetaData()
        self.meta.reflect(bind=self.engine)
        self.files = self.meta.tables["Files"]

    async def get_files(self) -> List[ArchiveFile]:
        query = self.files.select()
        rows = await self.fetch_all(query)
        try:
            files = parse_obj_as(List[ArchiveFile], rows)
        except ValidationError:
            raise FileParseError(
                "Failed to parse files as ArchiveFiles. Please reindex."
            )
        return files
