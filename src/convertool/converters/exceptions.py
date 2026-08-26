from subprocess import CalledProcessError
from subprocess import TimeoutExpired
from typing import Any

from acacore.models.file import BaseFile


class MissingDependency(Exception):
    def __init__(self, dependencies: list[str] | tuple[str, ...], *args: Any) -> None:  # noqa: ANN401
        self.dependencies: list[str] = list(dependencies)
        super().__init__(*dependencies, *args)


class UnsupportedPlatform(Exception):
    def __init__(self, platform: str, *args: Any) -> None:  # noqa: ANN401
        self.platform: str = platform
        super().__init__(platform, *args)


class UnsupportedOutput(Exception):
    def __init__(self, output: str, *args: Any) -> None:  # noqa: ANN401
        self.output: str = output
        super().__init__(output, *args)


class ConverterNotFound(Exception):
    def __init__(
        self,
        tool: str | None,
        output: str | None,
        via: list[str | tuple[str | None, str]] | None,
        *args,
    ) -> None:
        self.tool: str | None = tool
        self.output: str | None = output
        self.via: list[str | tuple[str | None, str]] | None = via
        super().__init__(*args)

    @property
    def tool_output(self) -> str | None:
        return f"{self.tool}:{self.output}" if self.tool or self.output else None


class BadOption(Exception): ...


class BadFile(Exception):
    def __init__(self, file: BaseFile, *args: object) -> None:
        self.file: BaseFile = file
        super().__init__(*args)


class BadDatabase(Exception): ...


class ConvertError(Exception):
    def __init__(
        self,
        file: BaseFile,
        msg: str | BaseException | None = None,
        process: CalledProcessError | TimeoutExpired | None = None,
        exception: Exception | None = None,
    ) -> None:
        self.file: BaseFile = file
        self.msg: str | BaseException | None = msg
        self.process: CalledProcessError | TimeoutExpired | None = process
        self.exception: Exception | None = exception
        super().__init__(msg)


class ConvertTimeoutError(ConvertError): ...


class OutputDirError(ConvertError): ...


class OutputTargetError(ConvertError): ...
