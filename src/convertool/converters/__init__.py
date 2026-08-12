from .base import ConverterABC
from .base import ConvertersEdge
from .base import ConvertersGraph
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

__all__ = [
    "ConverterABC",
    "ConvertersEdge",
    "ConvertersGraph",
    "ConvertersPath",
    "converters",
    "dummy_base_file",
]
