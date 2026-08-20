from base64 import b64encode
from contextlib import suppress
from pathlib import Path
from typing import ClassVar
from xml.sax.saxutils import escape
from zoneinfo import ZoneInfo

from acacore.models.file import BaseFile
from bs4 import BeautifulSoup
from chardet import detect as detect_encoding
from chardet import DetectionDict
from extract_msg import Message
from extract_msg import MSGFile
from extract_msg import openMsg
from extract_msg.attachments import WebAttachment
from extract_msg.enums import ErrorBehavior
from extract_msg.exceptions import ExMsgBaseException
from extract_msg.msg_classes import MessageBase
from extract_msg.msg_classes import MessageSigned
from striprtf.striprtf import rtf_to_text

from .base import ConverterABC
from .exceptions import ConvertError


# noinspection DuplicatedCode
def text_to_html(text: str) -> str:
    paragraphs = [p for p_raw in text.split("\n\n") if (p := p_raw.strip())]
    return "\n".join("<p>{}</p>\n".format(escape(p).replace("\n", "<br/>")) for p in paragraphs)


def html_to_text(html: str) -> str:
    return BeautifulSoup(html, "lxml").text.replace("\xa0", " ").strip()


def validate_msg(file: BaseFile) -> Message | MessageSigned:
    try:
        msg: MSGFile = openMsg(
            file.get_absolute_path(),
            delayAttachments=False,
            errorBehavior=ErrorBehavior.ATTACH_NOT_IMPLEMENTED,
        )
    except (ExMsgBaseException, OSError) as e:
        raise ConvertError(file, e.args[0] if e.args else "File cannot be opened as msg")

    if not isinstance(msg, Message | MessageSigned):
        raise ConvertError(file, f"Is of type {msg.__class__.__name__}")

    return msg


def msg_body(msg: MessageBase) -> tuple[str | None, str | None, str | None]:
    body_txt: str | None = None
    body_html: str | None = None
    body_rtf: str | None = None

    with suppress(AttributeError, UnicodeDecodeError):
        if msg.body is not None:
            body_txt = (msg.body or "").strip()

    with suppress(AttributeError, UnicodeDecodeError):
        if msg.htmlBody is not None and (encoding := detect_encoding(msg.htmlBody).get("encoding")):
            body_html = msg.htmlBody.decode(encoding)

    with suppress(AttributeError, UnicodeDecodeError):
        if msg.rtfBody is not None and (encoding := detect_encoding(msg.rtfBody).get("encoding")):
            body_rtf = msg.rtfBody.decode(encoding)

    return body_txt, body_html, body_rtf


# noinspection DuplicatedCode
def msg_front_matter(msg: MessageBase) -> str:
    attachment_names: list[str] = [a.longFilename for a in msg.attachments if getattr(a, "cid", None) is None]

    items: dict[str, str | list[str]] = {
        "From": msg.sender or "",
        "To": msg.to or "",
        "CC": msg.cc or "",
        "BCC": msg.bcc or "",
        "Date": msg.date.astimezone(ZoneInfo("UTC")).isoformat() if msg.date else "",
        "Subject": msg.subject or "",
        "Attachments": sorted(set(attachment_names), key=attachment_names.index),
    }

    text: str = ""

    text += "---\n"

    for header, value in items.items():
        text += f"{header}: "
        if isinstance(value, str):
            text += value
        elif len(value):
            text += "\n"
            text += "\n".join(f"  - {v}" for v in value)
        text += "\n"

    text += "---"

    return text


# noinspection DuplicatedCode
def msg_html_body(msg: MessageBase) -> str:
    body_plain, body_html, body_rtf = msg_body(msg)

    if not body_html and body_plain:
        body_html = text_to_html(body_plain.strip()).strip()
    elif not body_html and body_rtf:
        body_html = text_to_html(rtf_to_text(body_rtf, "cp1252", "replace").strip())

    body_html = body_html or "<html></html>"

    html = BeautifulSoup(body_html, "lxml")
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
    front_matter.string = msg_front_matter(msg)

    html.select_one("body").insert(0, front_matter)

    if not has_body:
        p = html.new_tag("p")
        p.string = "No readable content available."
        html.select_one("body").append(p)

    cids: dict[str, tuple[str, bytes]] = {}

    for a in msg.attachments:
        if isinstance(a, WebAttachment):
            continue
        if not (cid := getattr(a, "cid", None)) or not isinstance(a.data, bytes):
            continue
        cids[f"cid:{cid}"] = (a.mimetype or "", a.data)

    if cids:
        for tag in html.select("*"):
            for attr, value in tag.attrs.items():
                if not isinstance(value, str):
                    continue
                if attachment := cids.get(value):
                    data_b64: str = b64encode(attachment[1]).decode()
                    tag.attrs[attr] = f"data:{attachment[0]};base64,{data_b64}"

    return html.decode_contents()


def msg_plain_body(msg: MessageBase) -> str:
    plain, html, rtf = msg_body(msg)

    if not plain and html:
        plain = html_to_text(html).strip()
    elif not plain and rtf:
        plain = rtf_to_text(rtf, "cp1252", "replace").strip()

    plain = plain or "No readable content available."

    return f"{msg_front_matter(msg)}\n\n{plain.strip()}"


class MSGConverter(ConverterABC):
    name: ClassVar[str] = "msg"
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
        msg: Message | MessageSigned = validate_msg(self.file)

        try:
            body: str = ""

            if output == "html":
                body = msg_html_body(msg)
            elif output == "txt":
                body = msg_plain_body(msg)

            dest_dir.mkdir(parents=True, exist_ok=True)
            dest_file.write_text(body, encoding="utf-8")

            return [dest_file]
        except Exception as e:
            raise ConvertError(self.file, repr(e))
