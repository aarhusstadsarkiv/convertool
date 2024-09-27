from pathlib import Path
from typing import ClassVar

from acacore.models.file import File
from acacore.models.reference_files import TemplateTypeEnum

from .base import Converter
from .exceptions import ConvertError


class ConverterTemplate(Converter):
    tool_names: ClassVar[list[str]] = ["template"]
    outputs: ClassVar[list[str]] = TemplateTypeEnum

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)

        if output == "temporary-file":
            return []

        dest_dir: Path = self.output_dir(output_dir, keep_relative_path)
        dest_file: Path = self.output_file(dest_dir, "txt", append=True)

        if output == "text" and not self.file.action_data.ignore.reason:
            raise ConvertError(self.file, f"{output!r} template requires a reason")
        elif output == "text":
            dest_file.write_text(self.file.action_data.ignore.reason)
        elif output == "empty":
            dest_file.write_text("Den originale fil var tom")
        elif output == "password-protected":
            dest_file.write_text("Den originale fil var kodeordsbeskyttet")
        elif output == "corrupted":
            dest_file.write_text("Den originale fil var korrumperet og kunne ikke åbnes")
        elif output == "duplicate" and not self.database:
            raise ConvertError(self.file, f"{output!r} template requires a database")
        elif output == "duplicate":
            original: File | None = self.database.files.select(
                where="checksum = ? and action != 'ignore'",
                parameters=[self.file.checksum],
                limit=1,
            ).fetchone()
            dest_file.write_text(f"Den originale fil var en kopi af {original.relative_path}")
        elif output == "not-preservable":
            dest_file.write_text("Den originale fil var ikke bevaringsværdig")
        elif output == "not-convertable":
            dest_file.write_text("Den originale fil kunne ikke konverteres til et gyldigt arkivformat")
        elif output == "extracted-archive" and not self.database:
            raise ConvertError(self.file, f"{output!r} template requires a database")
        elif output == "extracted-archive":
            children: list[Path] = [
                f.relative_path
                for f in self.database.files.select(where="parent = ?", parameters=[str(self.file.uuid)])
            ]
            dest_file.write_text(
                "Den originale fil er udpakket, og indeholdt følgende filer:\n" + "\n".join(f"* {p}" for p in children)
            )

        return [dest_file]
