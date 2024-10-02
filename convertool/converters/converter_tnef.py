from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import ClassVar
from xml.sax.saxutils import escape

from bs4 import BeautifulSoup
from chardet import detect as detect_encoding
from striprtf.striprtf import rtf_to_text
from tnefparse import properties as tnefprops
from tnefparse import TNEF
from tnefparse import TNEFObject
from tnefparse.mapi import TNEFMAPI_Attribute

from .base import Converter
from .exceptions import ConvertError


@dataclass
class TNEFHeaders:
    subject: str | None = None
    date_sent: datetime | None = None
    from_name: str | None = None
    from_email: str | None = None
    to_name: str | None = None
    to_email: str | None = None


def text_to_html(text: str) -> str:
    paragraphs = [p for p_raw in text.split("\n\n") if (p := p_raw.strip())]
    return "\n".join("<p>{}</p>\n".format(escape(p).replace("\n", "<br/>")) for p in paragraphs)


def html_to_text(html: str) -> str:
    return BeautifulSoup(html, "lxml").text.replace("\xa0", " ").strip()


def tnef_object(tnef: TNEF, name: int) -> TNEFObject | None:
    return next((o for o in (tnef.objects + tnef.msgprops) if o.name == name), None)


def tnef_property(tnef: TNEF, name: int) -> TNEFMAPI_Attribute | None:
    return next((o for o in tnef.mapiprops if o.name == name), None)


def tnef_body_text(tnef: TNEF) -> str | None:
    if not tnef.has_body():
        return None

    if isinstance(tnef.body, bytes):
        return tnef.body.decode(tnef.codepage, "replace").strip()
    elif isinstance(tnef.body, str):
        return tnef.body.strip()
    elif tnef.htmlbody:
        return html_to_text(tnef.htmlbody)
    elif isinstance(tnef.rtfbody, bytes):
        if not detect_encoding(tnef.rtfbody)["encoding"]:
            return None
        return rtf_to_text(tnef.rtfbody.decode(tnef.codepage, "replace"), tnef.codepage, "replace").strip()
    elif isinstance(tnef.rtfbody, str):
        if not detect_encoding(tnef.rtfbody.encode(tnef.codepage))["encoding"]:
            return None
        return rtf_to_text(tnef.rtfbody, tnef.codepage, "replace").strip()
    else:
        return None


def tnef_body_html(tnef: TNEF) -> str | None:
    if not tnef.has_body():
        return None

    if tnef.htmlbody:
        return tnef.htmlbody.strip()
    else:
        return html_to_text(tnef_body_text(tnef))


def tnef_front_matter(tnef: TNEF, headers: TNEFHeaders) -> str:
    items: dict[str, str | list[str]] = {
        "From": f"{headers.from_name or ''} {f'<{headers.from_email}>' if headers.from_email else ''}".strip(),
        "To": f"{headers.to_name or ''} {f'<{headers.to_email}>' if headers.to_email else ''}".strip(),
        "Date": headers.date_sent.isoformat() if headers.date_sent else "",
        "Subject": headers.subject or "",
        "Attachments": [a.long_filename() for a in tnef.attachments],
    }

    text: str = ""

    text += "---\n"

    for header, value in items.items():
        text += f"{header}: "
        if isinstance(value, str):
            text += value
        else:
            text += "\n"
            text += "\n".join(f"  - {v}" for v in value)
        text += "\n"

    text += "---"

    return text


def tnef_to_txt(tnef: TNEF, headers: TNEFHeaders) -> str:
    text: str = tnef_front_matter(tnef, headers) + "\n\n"
    text += tnef_body_text(tnef) or "No readable content available."
    return text


def tnef_to_html(tnef: TNEF, headers: TNEFHeaders):
    if not (html_body := tnef_body_html(tnef) or "").strip():
        return (
            f"<html>"
            f'<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/></head>'
            f"<body><pre class='____front_matter'>{escape(tnef_front_matter(tnef, headers))}</pre>"
            f"<p>No readable content available.</p></body>"
            f"</html>"
        )
    else:
        html = BeautifulSoup(html_body, "lxml")
        has_body: bool = True

        if charset_tag := html.select_one('head > meta[http-equiv="Content-Type"]'):
            charset_tag.attrs["content"] = "text/html; charset=utf-8"

        if not html.select_one("body"):
            html.append(html.new_tag("body"))
            has_body = False

        front_matter = html.new_tag("pre", attrs={"class": "____front_matter"})
        front_matter.string = tnef_front_matter(tnef, headers)

        html.select_one("body").insert(0, front_matter)

        if not has_body:
            p = html.new_tag("p")
            p.string = "No readable content available."
            html.select_one("body").append(p)

        return html.decode_contents()


class ConverterTnef(Converter):
    tool_names: ClassVar[list[str]] = ["tnef"]
    outputs: ClassVar[list[[str]]] = ["html", "txt"]

    def convert(self, output_dir: Path, output: str, *, keep_relative_path: bool = True) -> list[Path]:
        output = self.output(output)
        dest_dir: Path = self.output_dir(output_dir, keep_relative_path)
        dest_file: Path = self.output_file(dest_dir, output)

        try:
            with self.file.get_absolute_path().open("rb") as fh:
                tnef = TNEF(fh.read())

            obj_subject = tnef_object(tnef, tnef.ATTSUBJECT)
            obj_date_sent = tnef_object(tnef, tnef.ATTDATESENT)
            obj_sender_name = tnef_property(tnef, tnefprops.MAPI_SENDER_NAME)
            obj_sender_email = tnef_property(tnef, tnefprops.MAPI_SENDER_EMAIL_ADDRESS)
            obj_receiver_name = tnef_property(tnef, tnefprops.MAPI_RECEIVED_BY_NAME)
            obj_receiver_email = tnef_property(tnef, tnefprops.MAPI_RECEIVED_BY_EMAIL_ADDRESS)

            headers = TNEFHeaders(
                subject=obj_subject.data if obj_subject else "",
                from_name=obj_sender_name.data if obj_sender_name else "",
                from_email=obj_sender_email.data if obj_sender_email else "",
                to_name=obj_receiver_name.data if obj_receiver_name else "",
                to_email=obj_receiver_email.data if obj_receiver_email else "",
                date_sent=obj_date_sent.data if obj_date_sent else "",
            )

            if output == "txt":
                dest_file.write_text(tnef_to_txt(tnef, headers), encoding="utf-8")
            elif output == "html":
                dest_file.write_text(tnef_to_html(tnef, headers), encoding="utf-8")

            return [dest_file]
        except Exception as e:
            raise ConvertError(self.file, repr(e))
