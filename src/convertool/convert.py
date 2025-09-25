from logging import ERROR
from logging import INFO
from multiprocessing import Pool
from pathlib import Path
from typing import Any
from typing import Literal
from typing import NamedTuple

from acacore.database import FilesDB
from acacore.models.event import Event
from acacore.models.file import AccessFile
from acacore.models.file import ConvertedFile
from acacore.models.file import MasterFile
from acacore.models.file import OriginalFile
from acacore.models.file import StatutoryFile
from acacore.utils.click import context_commands
from acacore.utils.helpers import ExceptionManager
from click import Context
from structlog.stdlib import BoundLogger

from . import converters
from .converters.exceptions import ConverterNotFound
from .converters.exceptions import ConvertError
from .converters.exceptions import ConvertTimeoutError
from .converters.exceptions import OutputDirError
from .converters.exceptions import OutputTargetError


class ConvertInstructions[M: OriginalFile | MasterFile, O: ConvertedFile](NamedTuple):
    file: M
    file_type: Literal["original", "master"]
    dest_type: Literal["master", "access", "statutory"]
    converter_cls: type[converters.ConverterABC]
    tool: str
    output: str
    options: dict[str, Any] | None
    output_cls: type[O]


def find_converter(tool: str, output: str) -> type[converters.ConverterABC] | None:
    for converter in (
        converters.ConverterCopy,
        converters.ConverterTemplate,
        converters.ConverterSymphovert,
        converters.ConverterGIS,
        converters.ConverterHTML,
        converters.ConverterHTMLToImage,
        converters.ConverterCAD,
        converters.ConverterTNEF,
        converters.ConverterMedCom,
        converters.ConverterMedComToImage,
        converters.ConverterMedComToPDF,
        converters.ConverterMSG,
        converters.ConverterMSGToImage,
        converters.ConverterMSGToPDF,
        converters.ConverterMSExcel,
        converters.ConverterMSPowerPoint,
        converters.ConverterMSWord,
        converters.ConverterDocument,
        converters.ConverterDocumentToImage,
        converters.ConverterPresentation,
        converters.ConverterSpreadsheet,
        converters.ConverterSAS,
        converters.ConverterPDFToImage,
        converters.ConverterPDFLargeToImage,
        converters.ConverterTextToImage,
        converters.ConverterImage,
        converters.ConverterAudio,
        converters.ConverterVideo,
        converters.ConverterPDF,
        converters.ConverterXSL,
        converters.ConverterXSLToImage,
        converters.ConverterXSLToPDF,
        converters.ConverterZIPFile,
    ):
        if converter.match_tool(tool, output):
            return converter

    return None


def original_file_converter(file: OriginalFile) -> ConvertInstructions[OriginalFile, MasterFile]:
    """
    Get conversion instructions for original file.

    :param file:
    :return: converter class, tool, output, options
    """
    if file.action == "convert" and not file.action_data.convert:
        raise ConverterNotFound(None, None, "Missing convert action data")
    if file.action == "convert":
        tool, output, options = (
            file.action_data.convert.tool,
            file.action_data.convert.output,
            file.action_data.convert.options,
        )
        converter_cls = find_converter(tool, output)
    elif file.action == "ignore" and not file.action_data.ignore:
        raise ConverterNotFound(None, None, "Missing ignore action data")
    elif file.action == "ignore":
        tool, output, options = "template", file.action_data.ignore.template, None
        converter_cls = find_converter(tool, output)
    else:
        raise ValueError(f"Unsupported action {file.action!r}")

    if not converter_cls:
        raise ConverterNotFound(tool, output, f"No converter found for tool {tool!r} and output {output!r}")

    # noinspection PyTypeChecker
    return ConvertInstructions(file, "original", "master", converter_cls, tool, output, options, MasterFile)


def master_file_converter(
    file: MasterFile,
    dest_type: Literal["access", "statutory"],
) -> ConvertInstructions[MasterFile, AccessFile | StatutoryFile]:
    """
    Get conversion instructions for master file.

    :param file:
    :param dest_type:
    :return: converter class, tool, output, options
    """
    if dest_type == "access" and not file.convert_access:
        raise ConverterNotFound(None, None, "Missing convert action data")
    if dest_type == "access":
        tool, output, options = (
            file.convert_access.tool,
            file.convert_access.output,
            file.convert_access.options,
        )
        converter_cls = find_converter(tool, output)
        output_cls = ConvertedFile
    elif dest_type == "statutory" and not file.convert_statutory:
        raise ConverterNotFound(None, None, "Missing convert action data")
    elif dest_type == "statutory":
        tool, output, options = (
            file.convert_statutory.tool,
            file.convert_statutory.output,
            file.convert_statutory.options,
        )
        converter_cls = find_converter(tool, output)
        output_cls = StatutoryFile

    if not converter_cls:
        raise ConverterNotFound(tool, output, f"No converter found for tool {tool!r} and output {output!r}")

    return ConvertInstructions(file, "master", dest_type, converter_cls, tool, output, options, output_cls)


def file_queues[M: OriginalFile | MasterFile, O: ConvertedFile](
    instructions: list[ConvertInstructions[M, O]],
    threads: int,
) -> tuple[list[ConvertInstructions[M, O]], list[list[ConvertInstructions[M, O]]]]:
    """
    Create conversion queues.

    :param instructions:
    :param threads:
    :return: synchronous queue, asynchronous queue
    """
    sync_queue: list[ConvertInstructions[M, O]] = []
    async_queues: list[list[ConvertInstructions[M, O]]] = [[]]

    for inst in instructions:
        if threads <= 1 or not inst.converter_cls.multithreading:
            sync_queue.append(inst)
        elif len(async_queues[-1]) < threads:
            async_queues[-1].append(inst)
        else:
            async_queues.append([])
            async_queues[-1].append(inst)

    return sync_queue, async_queues


def convert[M: OriginalFile | MasterFile, O: MasterFile | AccessFile | StatutoryFile](
    context: Context | str,
    database: FilesDB | None,
    output_dir: Path,
    instructions: ConvertInstructions[M, O],
    verbose: bool,
    logger: BoundLogger,
) -> tuple[ConvertInstructions[M, O], list[ConvertedFile], ExceptionManager | None]:
    output_paths: list[Path] = []

    with ExceptionManager(BaseException) as exception:
        converter = instructions.converter_cls(
            file=instructions.file,
            database=database,
            options=instructions.options,
            capture_output=not verbose,
        )

        Event.from_command(context, "run", instructions.file).log(
            INFO,
            logger,
            converter=f"{instructions.tool}:{instructions.output}",
            name=instructions.file.name,
        )

        output_paths = converter.convert(output_dir, instructions.output, keep_relative_path=True)
        output_files = [
            instructions.output_cls.from_file(p, output_dir, {"original_uuid": instructions.file.uuid, "sequence": n})
            for n, p in enumerate(output_paths)
        ]

        for file in output_files:
            Event.from_command(context, "out", file).log(
                INFO,
                logger,
                converter=f"{instructions.tool}:{instructions.output}",
                original=instructions.file.name,
                name=file.name,
            )

        return instructions, output_files, None

    if exception.exception is not None:
        for p in output_paths:
            p.unlink(missing_ok=True)
        log_args: dict[str, Any] = {}
        if isinstance(exception.exception, ConvertTimeoutError):
            log_args["timeout"] = converter.process_timeout
        elif isinstance(exception.exception, OutputDirError | OutputTargetError):
            log_args["reason"] = exception.exception.msg
        elif isinstance(exception.exception, ConvertError):
            if isinstance(exception.exception.msg, BaseException):
                log_args["exc_info"] = exception.exception.msg
            elif exception.exception.msg:
                log_args["msg"] = ""
            if verbose and exception.exception.process:
                log_args["stderr"] = exception.exception.process.stderr or exception.exception.process.stderr or ""
        elif isinstance(exception.exception, Exception):
            log_args["msg"] = " ".join(map(str, exception.exception.args)) or ""
            log_args["exc_info"] = exception.exception
        elif isinstance(exception.exception, BaseException):
            raise exception.exception
        Event.from_command(context, "error", instructions.file).log(
            ERROR,
            logger,
            converter=f"{instructions.tool}:{instructions.output}",
            error=exception.exception.__class__.__name__,
            **log_args,
        )

    return instructions, [], exception


def convert_async_queue[M: OriginalFile | MasterFile, O: MasterFile | AccessFile | StatutoryFile](
    context: Context | str,
    database: FilesDB | None,
    output_dir: Path,
    instructions: list[ConvertInstructions[M, O]],
    threads: int,
    verbose: bool,
    logger: BoundLogger,
) -> list[tuple[ConvertInstructions[M, O], list[ConvertedFile], ExceptionManager | None]]:
    context_str: str = ".".join(context_commands(context)) if isinstance(context, Context) else context
    with Pool(threads) as pool:
        args = [(context_str, database, output_dir, inst, verbose, logger) for inst in instructions]
        results = pool.starmap(convert, args)
        pool.close()
        pool.join()

    return results


def convert_queue[M: OriginalFile | MasterFile, O: MasterFile | AccessFile | StatutoryFile](
    context: Context | str,
    database: FilesDB | None,
    output_dir: Path,
    queue: list[ConvertInstructions[M, O]],
    verbose: bool,
    logger: BoundLogger,
) -> list[tuple[ConvertInstructions[M, O], list[ConvertedFile], ExceptionManager | None]]:
    context_str: str = ".".join(context_commands(context)) if isinstance(context, Context) else context
    return [convert(context_str, database, output_dir, inst, verbose, logger) for inst in queue]
