from pathlib import Path
from typing import ClassVar

from bs4 import BeautifulSoup
from eml_analyzer.library.parser import Attachment
from eml_analyzer.library.parser import ParsedEmail

from convertool.util import TempDir

from .base import _shared_dependencies
from .base import _shared_platforms
from .base import _shared_process_timeout
from .base import ConverterABC
from .base import dummy_base_file
from .converter_html import ConverterHTMLToImage
from .converter_msg import html_to_text
from .converter_msg import text_to_html
from .exceptions import OutputTargetError


def eml_front_matter(eml: ParsedEmail, attachments: list[tuple[str | None, Attachment]]) -> str:
    header: list[tuple[str, str | list[str]]] = [
        *((name, str(value)) for name, value in eml.get_header() if name.lower() != "content-type"),
        (
            "Attachments",
            sorted(
                a.filename or f"attachment-{n:02}"
                for n, [_, a] in enumerate(attachments, 1)
                if a.content_disposition == "attachment"
            ),
        ),
    ]

    text: str = ""

    text += "---\n"

    for header, value in header:
        text += f"{header}: "
        if isinstance(value, str):
            text += value
        elif len(value):
            text += "\n"
            text += "\n".join(f"  - {v}" for v in value)
        text += "\n"

    text += "---"

    return text


def eml_attachments(eml: ParsedEmail) -> list[tuple[str | None, Attachment]]:
    attachments: list[tuple[str | None, Attachment]] = []
    counter: int = 0

    # noinspection PyProtectedMember
    for item in eml._parsed_email.walk():
        if item.get_filename() is None:
            continue
        headers: dict[str, str] = {h.lower(): v for h, v in getattr(item, "_headers", [])}
        content_id = content_id.strip("<>") if (content_id := headers.get("content-id")) else None
        counter += 1
        attachments.append((content_id, Attachment(message=item, index=counter)))

    return attachments


# noinspection DuplicatedCode
def eml_html_body(eml: ParsedEmail) -> str:
    plain, html = eml.get_text_content(), eml.get_html_content()
    attachments = eml_attachments(eml)

    if not html and plain:
        html = text_to_html(plain.strip()).strip()

    html = html or "<html></html>"

    html = BeautifulSoup(html, "lxml")
    has_body: bool = True

    if not html.select_one("head"):
        html.append(html.new_tag("head"))

    if charset_tag := html.select_one('head > meta[http-equiv="Content-Type"]'):
        charset_tag.attrs["content"] = "text/html; charset=utf-8"
    else:
        html.select_one("head").append(
            html.new_tag(
                "meta",
                attrs={"http-equiv": "Content-Type", "content": "text/html; charset=utf-8"},
            )
        )

    if not html.select_one("body"):
        html.append(html.new_tag("body"))
        has_body = False

    front_matter = html.new_tag("pre", attrs={"class": "____front_matter"})
    front_matter.string = eml_front_matter(eml, attachments)

    html.select_one("body").insert(0, front_matter)

    if not has_body:
        p = html.new_tag("p")
        p.string = "No readable content available."
        html.select_one("body").append(p)

    cids: dict[str, Attachment] = {f"cid:{cid}": a for cid, a in attachments if cid is not None}

    if cids:
        for tag in html.select("*"):
            for attr, value in tag.attrs.items():
                if not isinstance(value, str):
                    continue
                if attachment := cids.get(value):
                    tag.attrs[attr] = (
                        f"data:{attachment.content_type or ''};base64,{attachment.get_content_base64_encoded()}"
                    )

    return html.decode_contents()


def eml_plain_body(eml: ParsedEmail) -> str:
    plain, html = eml.get_text_content(), eml.get_html_content()

    if html:
        plain = html_to_text(html).strip()

    plain: str = plain or "No readable content available."

    return f"{eml_front_matter(eml, eml_attachments(eml))}\n\n{plain.strip()}"


class ConverterEML(ConverterABC):
    tool_names: ClassVar[list[str]] = ["eml"]
    outputs: ClassVar[list[str]] = ["html", "txt"]

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = self.output_file(dest_dir, output)

        eml = ParsedEmail(
            self.file.get_absolute_path().read_text(self.file.encoding["encoding"] if self.file.encoding else None)
        )

        body: str

        if output == "html":
            body = eml_html_body(eml)
        elif output == "txt":
            body = eml_plain_body(eml)
        else:
            raise OutputTargetError(self.file, f"Unsupported output {output}")

        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_file.write_text(body, "utf-8")

        return [dest_file]


class ConverterEMLToImage(ConverterABC):
    tool_names: ClassVar[list[str]] = ConverterEML.tool_names
    outputs: ClassVar[list[str]] = ConverterHTMLToImage.outputs
    platforms: ClassVar[list[str] | None] = _shared_platforms(ConverterEML, ConverterHTMLToImage)
    dependencies: ClassVar[dict[str, list[str]] | None] = _shared_dependencies(ConverterEML, ConverterHTMLToImage)
    process_timeout: ClassVar[float | None] = _shared_process_timeout(ConverterEML, ConverterHTMLToImage)

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)

        with TempDir(output_dir) as tmp_dir:
            if not (
                htmls := ConverterEML(
                    self.file,
                    self.database,
                    self.file.root,
                    hashed_output_name=self.hashed_output_name,
                ).convert(tmp_dir, "html", keep_relative_path=keep_relative_path)
            ):
                return []

            html = htmls[0]

            return ConverterHTMLToImage(
                dummy_base_file(html, tmp_dir),
                self.database,
                tmp_dir,
                hashed_output_name=self.hashed_output_name,
            ).convert(output_dir, output, keep_relative_path=keep_relative_path)
