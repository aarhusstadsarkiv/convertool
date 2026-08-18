from datetime import datetime
from pathlib import Path

import pytest
from acacore.database import FilesDB
from acacore.models.file import OriginalFile
from acacore.models.reference_files import ActionData
from acacore.models.reference_files import IgnoreAction
from acacore.models.reference_files import TemplateTypeEnum
from acacore.models.reference_files import TTemplateType

from convertool.converters import TemplateConverter
from convertool.converters.exceptions import ConvertError
from convertool.util import AVID


def test_template(test_files: dict[str, Path], reference_files: dict[str, Path], avid_dir_copy: Path, output_dir: Path):
    avid = AVID(avid_dir_copy)

    with FilesDB(avid.database_path) as db:
        file = OriginalFile(
            checksum="",
            encoding=None,
            relative_path=Path("template.jpg"),
            original_path=Path("template.jpg"),
            is_binary=False,
            size=0,
            puid=None,
            signature=None,
            action="ignore",
            action_data=ActionData(),
            root=output_dir,
        )
        converter = TemplateConverter(file, output_dir, database=db, hashed_output_name=False)
        templates: list[TTemplateType] = [
            t for t in TemplateTypeEnum if t in TemplateConverter.outputs and t not in ["duplicate"]
        ]

        for template in templates:
            print(template)
            reason: str = f"Template {template} test at {datetime.now().isoformat()}"
            converter.file.relative_path = Path(f"template-{template}.jpg")
            converter.file.action_data.ignore = IgnoreAction(template=template, reason=reason)
            output_files = converter.convert(output_dir, template)
            if template == "temporary-file":
                assert not output_files
                continue

            assert len(output_files) == 1
            assert output_files[0].name == converter.file.relative_path.name + ".txt"
            if template == "text":
                assert output_files[0].read_text() == reason
            else:
                assert output_files[0].read_text() == reference_files[output_files[0].name].read_text()


def test_template_errors(avid_dir_copy: Path, output_dir: Path):
    avid = AVID(avid_dir_copy)

    with FilesDB(avid.database_path) as db:
        file = OriginalFile(
            checksum="",
            encoding=None,
            relative_path=Path("template.jpg"),
            original_path=Path("template.jpg"),
            is_binary=False,
            size=0,
            puid=None,
            signature=None,
            action="ignore",
            action_data=ActionData(),
            root=output_dir,
        )
        converter = TemplateConverter(file, output_dir, database=db)
        templates: list[TTemplateType] = ["duplicate"]

        for template in templates:
            with pytest.raises(ConvertError):
                converter.file.action_data.ignore = IgnoreAction(template=template)
                converter.convert(output_dir, template)
