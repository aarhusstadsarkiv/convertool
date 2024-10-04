from click import File


class ConvertError(Exception):
    def __init__(self, file: File, msg: str | BaseException | None = None) -> None:
        self.file: File = file
        self.msg: str | BaseException | None = msg
        super().__init__(msg)


class ConvertTimeoutError(ConvertError): ...


class OutputDirError(ConvertError): ...


class OutputExtensionError(ConvertError): ...
