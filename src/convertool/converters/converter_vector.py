from typing import ClassVar

from .converter_html import HTMLConverter


class VectorConverter(HTMLConverter):
    name: ClassVar[str] = "vector"
