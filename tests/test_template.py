from datetime import datetime
from pathlib import Path

import pytest
from acacore.models.file import File
from acacore.models.reference_files import ActionData
from acacore.models.reference_files import IgnoreAction

from convertool.converters import ConverterTemplate
from convertool.converters.exceptions import ConvertError


def test_templates(test_files: dict[str, Path], reference_files: dict[str, Path], output_dir: Path):
    file = File(
        checksum="",
        relative_path=Path("template.jpg"),
        is_binary=False,
        size=0,
        puid=None,
        signature=None,
        action="ignore",
        action_data=ActionData(),
        root=output_dir,
    )
    converter = ConverterTemplate(file)
    templates = [t for t in ConverterTemplate.outputs if t not in ["duplicate", "extracted-archive"]]

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


def test_template_errors(output_dir: Path):
    file = File(
        checksum="",
        relative_path=Path("template.jpg"),
        is_binary=False,
        size=0,
        puid=None,
        signature=None,
        action="ignore",
        action_data=ActionData(),
        root=output_dir,
    )
    converter = ConverterTemplate(file)

    for template in ["duplicate", "extracted-archive"]:
        with pytest.raises(ConvertError):
            converter.file.action_data.ignore = IgnoreAction(template=template)
            converter.convert(output_dir, template)
