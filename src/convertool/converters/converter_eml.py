from pathlib import Path
from typing import ClassVar

from bs4 import BeautifulSoup
from chardet import DetectionDict
from eml_analyzer.library.parser import Attachment
from eml_analyzer.library.parser import ParsedEmail

from .base import ConverterABC
from .converter_msg import html_to_text
from .converter_msg import text_to_html
from .exceptions import OutputTargetError


def eml_front_matter(eml: ParsedEmail, attachments: list[tuple[str | None, Attachment]]) -> str:
    headers: dict[str, str] = {k.lower(): str(v) for k, v in eml.get_header()}
    header: list[tuple[str, str | list[str]]] = [
        ("From", headers.get("from", "")),
        ("To", headers.get("to", "")),
        ("CC", headers.get("cc", "")),
        ("BCC", headers.get("bcc", "")),
        ("Date", headers.get("date", "")),
        ("Subject", headers.get("subject", "")),
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


class EMLConverter(ConverterABC):
    name: ClassVar[str] = "eml"
    outputs: ClassVar[list[str]] = ["html", "txt"]

    @classmethod
    def output_name(cls, output: str) -> str:
        if output == "html":
            return "html"
        if output == "txt":
            return "text"
        return output

    def output_extension(self, output: str) -> str:
        if output == "html":
            return ".html"
        if output == "txt":
            return ".txt"
        return f".{output}"

    def output_puid(self, output: str) -> str | None:
        if output == "html":
            return "fmt/471"
        if output == "txt":
            return "x-fmt/111"
        return None

    def output_encoding(self, output: str) -> DetectionDict | None:
        if output == "txt":
            return DetectionDict(encoding="utf-8", confidence=1.0, language=None, mime_type="text/plain")
        if output == "html":
            return DetectionDict(encoding="utf-8", confidence=1.0, language=None, mime_type="text/html")
        return None

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        self.test_output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path=keep_relative_path)
        dest_file: Path = dest_dir.joinpath(self.output_filename(output))

        eml = ParsedEmail(self.read_text())

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
