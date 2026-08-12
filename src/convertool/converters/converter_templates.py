from pathlib import Path
from typing import ClassVar

from acacore.models.file import BaseFile
from acacore.models.file import OriginalFile
from acacore.models.reference_files import TemplateTypeEnum
from chardet import DetectionDict

from .base import ConverterABC
from .exceptions import ConvertError


class TemplateConverter(ConverterABC):
    name: ClassVar[str] = "template"
    outputs: ClassVar[list[str]] = list(TemplateTypeEnum)
    requires_file_classes: ClassVar[list[type[BaseFile]]] = [OriginalFile]
    requires_database: ClassVar[bool] = True

    @classmethod
    def output_name(cls, output: str) -> str:
        return "text"

    def output_extension(self, output: str) -> str:
        return ".txt"

    def output_puid(self, output: str) -> str | None:
        if output == "temporary-file":
            return None
        return "x-fmt/111"

    def output_encoding(self, output: str) -> DetectionDict | None:
        if output == "temporary-file":
            return None
        return DetectionDict(encoding="utf-8", confidence=1.0, language=None, mime_type="text/plain")

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        self.test_output(output)

        if not isinstance(self.file, OriginalFile):
            raise ConvertError(self.file, f"{self.name!r} converter requires OriginalFile")
        if not self.file.action_data.ignore:
            raise ConvertError(self.file, f"{self.name!r} converter requires action 'ignore'")

        if output == "temporary-file":
            return []

        template: str = ""

        if output == "text":
            if self.file.action_data.ignore.reason is None:
                raise ConvertError(self.file, f"{output!r} template requires a reason")
            template = self.file.action_data.ignore.reason
        elif output == "empty":
            template = "Den originale fil var tom."
        elif output == "password-protected":
            template = "Den originale fil var kodeordsbeskyttet."
        elif output == "corrupted":
            template = "Den originale fil var korrumperet og kunne ikke åbnes."
        elif output == "duplicate" and not self.database:
            raise ConvertError(self.file, f"{output!r} template requires a database")
        elif output == "duplicate":
            if isinstance(self.file, OriginalFile):
                raise ConvertError(self.file, f"{output!r} template requires OriginalFile")

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
        elif output == "unidentified":
            template = "Den originale fil kunne ikke genkendes og derfor ikke konverteres til et gyldigt arkivformat."
        elif output == "extracted-archive":
            if self.database is None:
                raise ConvertError(self.file, f"{output!r} template requires a database")

            children: list[Path] = [
                f.relative_path for f in self.database.original_files.select({"parent": str(self.file.uuid)})
            ]

            template = "Den originale fil er udpakket, og indeholdt følgende filer:\n" + "\n".join(
                f"* {p}" for p in children
            )

        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = dest_dir.joinpath(self.output_filename(output, append=True))

        dest_file.parent.mkdir(parents=True, exist_ok=True)
        dest_file.write_text(template, encoding="utf-8")

        return [dest_file]
