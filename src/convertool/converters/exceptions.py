from subprocess import CalledProcessError
from subprocess import TimeoutExpired
from typing import Any

from acacore.models.file import BaseFile


class MissingDependency(Exception): ...


class UnsupportedPlatform(Exception): ...


class ConverterNotFound(Exception):
    def __init__(self, tool: str | None, output: str | None, *args: Any):
        self.tool: str | None = tool
        self.output: str | None = output
        super().__init__(*args)

    @property
    def tool_output(self) -> str | None:
        return f"{self.tool}:{self.output}" if self.tool or self.output else None


class BadOption(Exception): ...


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
