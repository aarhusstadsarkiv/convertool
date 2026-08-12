from collections.abc import Callable

from acacore.models.file import BaseFile

from .base import ConverterABC
from .base import ConvertersEdge
from .base import ConvertersPath
from .base import dummy_base_file
from .converter_audio import AudioConverter
from .converter_cad import CADConverter
from .converter_copy import CopyConverter
from .converter_document import DocumentConverter
from .converter_eml import EMLConverter
from .converter_gis import GISConverter
from .converter_html import HTMLConverter
from .converter_image import ImageConverter
from .converter_mdi import MDIConverter
from .converter_msg import MSGConverter
from .converter_msoffice import MSExcelConverter
from .converter_msoffice import MSPowerPointConverter
from .converter_msoffice import MSWordConverter
from .converter_notebook import IPYNBConverter
from .converter_pdf import PDFConverter
from .converter_pdf import PDFToImageConverter
from .converter_pdf import PDFToImageFallbackConverter
from .converter_presentation import PresentationConverter
from .converter_sas import SASConverter
from .converter_spreadsheet import SpreadsheetConverter
from .converter_symphovert import SymphovertConverter
from .converter_templates import TemplateConverter
from .converter_text import TextConverter
from .converter_text import TextToDocumentConverter
from .converter_tnef import TNEFConverter
from .converter_vector import VectorConverter
from .converter_video import VideoConverter
from .converter_xsl import MedComConverter
from .converter_xsl import XSLConverter
from .converter_zipfile import ZIPFileConverter
from .exceptions import MissingDependency
from .exceptions import UnsupportedPlatform

converters: list[type[ConverterABC]] = [
    AudioConverter,
    CADConverter,
    CopyConverter,
    DocumentConverter,
    EMLConverter,
    GISConverter,
    HTMLConverter,
    ImageConverter,
    IPYNBConverter,
    MDIConverter,
    MSExcelConverter,
    MSGConverter,
    MSPowerPointConverter,
    MSWordConverter,
    MedComConverter,
    PDFConverter,
    PDFToImageConverter,
    PDFToImageFallbackConverter,
    PresentationConverter,
    SASConverter,
    SpreadsheetConverter,
    SymphovertConverter,
    TemplateConverter,
    TextConverter,
    TextToDocumentConverter,
    TNEFConverter,
    VectorConverter,
    VideoConverter,
    XSLConverter,
    ZIPFileConverter,
]


def _instantiate[R](f: Callable[[], R]) -> R:
    return f()


@_instantiate
def conversion_graph() -> dict[tuple[str, str], list[ConvertersPath]]:
    def _compute_converter_branches(
        _conv: type[ConverterABC],
        _prev_edges: list[ConvertersEdge] | None = None,
        _prev_platforms: list[str] | None = None,
    ) -> list[ConvertersPath]:
        conv_paths: list[ConvertersPath] = []

        if _conv.platforms and _prev_platforms and not set(_prev_platforms).intersection(_conv.platforms):
            return []

        for output in _conv.outputs:
            edge = ConvertersEdge(_conv, output)

            if _prev_edges and edge in _prev_edges:
                continue

            conv_paths.append(ConvertersPath(_conv.name, output, [edge]))

            conv_paths.extend(
                [
                    ConvertersPath(_conv.name, b.output, [edge, *b.branch])
                    for c in converters
                    if (c.requires_file_classes is None or BaseFile in c.requires_file_classes)
                    and (_conv.requires_database or not c.requires_database)
                    and c.name == _conv.output_name(output)
                    for b in _compute_converter_branches(
                        c,
                        [
                            *(_prev_edges or []),
                            *(ConvertersEdge(_conv, _o) for _o in _conv.outputs),
                        ],
                        [
                            *(_prev_platforms or []),
                            *(_conv.platforms or []),
                        ],
                    )
                ]
            )

        return list(set(conv_paths))

    paths: dict[tuple[str, str], list[ConvertersPath]] = {}

    for conv in converters:
        for path in _compute_converter_branches(conv, []):
            key = (path.name, path.output)
            paths[key] = [*paths.get(key, []), path]

    return {(k[0], k[1]): bs for k, bs in paths.items()}


def filter_conversion_graph() -> dict[tuple[str, str], list[ConvertersPath]]:
    graph: dict[tuple[str, str], list[ConvertersPath]] = {}

    for key, paths in conversion_graph.items():
        valid_paths: list[ConvertersPath] = []

        for p in paths:
            try:
                p.test()
            except (MissingDependency, UnsupportedPlatform):
                continue

            valid_paths.append(p)

        if valid_paths:
            graph[key] = valid_paths

    return graph


__all__ = [
    "ConverterABC",
    "ConvertersEdge",
    "ConvertersPath",
    "conversion_graph",
    "converters",
    "dummy_base_file",
    "filter_conversion_graph",
]
