"""Custom exceptions defined for use in convertool modules.

"""
# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------


class ConvertoolError(Exception):
    """Base class for convertool errors."""


class ConversionError(ConvertoolError):
    """Implements an error to raise when conversion fails."""


class WrongOSError(ConvertoolError):
    """Implements an error to raise when the OS is not supported."""


class ProcessError(ConvertoolError):
    """Implements an error to raise when a process emits errors."""


class LibreError(ConvertoolError):
    """Implements an error to raise when LibreOffice or related
    functionality fails."""

    def __init__(self, message: str, timeout: bool = False):
        super().__init__(message)
        self.timeout = timeout


class LibreNotFoundError(ConvertoolError):
    """Implements an error to raise when LibreOffice
    is not found on the system."""


class GSNotFoundError(ConvertoolError):
    """Implements an error to raise when Ghostscript
    is not found on the system."""


class GSError(ConvertoolError):
    """Implements an error to raise when Ghostscript
    functionality fails."""


class ImageError(ConvertoolError):
    """Implements an error to raise when image conversion fails."""


class FileParseError(ConvertoolError):
    """Implements an error to raise if file parsing fails"""
