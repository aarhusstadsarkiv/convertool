from subprocess import CalledProcessError
from subprocess import TimeoutExpired

from acacore.models.file import BaseFile


class MissingDependency(Exception): ...


class UnsupportedPlatform(Exception): ...


class ConvertError(Exception):
    def __init__(
        self,
        file: BaseFile,
        msg: str | BaseException | None = None,
        process: CalledProcessError | TimeoutExpired | None = None,
    ) -> None:
        self.file: BaseFile = file
        self.msg: str | BaseException | None = msg
        self.process: CalledProcessError | TimeoutExpired | None = process
        super().__init__(msg)


class ConvertTimeoutError(ConvertError): ...


class OutputDirError(ConvertError): ...


class OutputTargetError(ConvertError): ...
