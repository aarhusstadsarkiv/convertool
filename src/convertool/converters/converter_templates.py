from pathlib import Path
from typing import ClassVar

from acacore.models.file import OriginalFile
from acacore.models.reference_files import TemplateTypeEnum

from .base import ConverterABC
from .exceptions import ConvertError


class ConverterTemplate(ConverterABC):
    tool_names: ClassVar[list[str]] = ["template"]
    outputs: ClassVar[list[str]] = TemplateTypeEnum

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)

        if output == "temporary-file":
            return []

        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = self.output_file(dest_dir, "txt", append=True)

        template: str = ""

        if output == "text" and not self.file.action_data.ignore.reason:
            raise ConvertError(self.file, f"{output!r} template requires a reason")
        if output == "text":
            template = self.file.action_data.ignore.reason
        elif output == "empty":
            template = "Den originale fil var tom."
        elif output == "password-protected":
            template = "Den originale fil var kodeordsbeskyttet."
        elif output == "corrupted":
            template = "Den originale fil var korrumperet og kunne ikke åbnes."
        elif output == "duplicate" and not self.database:
            raise ConvertError(self.file, f"{output!r} template requires a database")
        elif output == "duplicate" and not isinstance(self.file, OriginalFile):
            raise ConvertError(self.file, f"{output!r} template requires OriginalFile")
        elif output == "duplicate":
            if not (
                original := self.database.original_files.select(
                    "checksum = ? and action != 'ignore'",
                    [self.file.checksum],
                    limit=1,
                ).fetchone()
            ):
                raise ConvertError(self.file, f"{output!r} template requires a non-ignored duplicate")
            template = f"Den originale fil var en kopi af {original.relative_path}."
        elif output == "not-preservable":
            template = "Den originale fil var ikke bevaringsværdig."
        elif output == "not-convertable":
            template = "Den originale fil kunne ikke konverteres til et gyldigt arkivformat."
        elif output == "extracted-archive" and not self.database:
            raise ConvertError(self.file, f"{output!r} template requires a database")
        elif output == "extracted-archive":
            children: list[Path] = [
                f.relative_path for f in self.database.original_files.select({"parent": str(self.file.uuid)})
            ]
            template = "Den originale fil er udpakket, og indeholdt følgende filer:\n" + "\n".join(
                f"* {p}" for p in children
            )

        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_file.write_text(template, encoding="utf-8")

        return [dest_file]
