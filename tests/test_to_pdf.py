from json import loads
from pathlib import Path
from subprocess import run

from acacore.models.file import File

from convertool.converters.converter_to_pdf import ConverterToPDF


# noinspection DuplicatedCode
def test_pdf_to_pdfa(test_files: dict[str, Path], reference_files: dict[str, Path], output_dir: Path):
    file = File.from_file(test_files["pdf-to-pdfa.pdf"], root=test_files["pdf-to-pdfa.pdf"].parent)
    converter = ConverterToPDF(file)

    for pdfa_ver in (1, 2, 3):
        output: str = f"pdfa-{pdfa_ver}"
        print(output)
        output_files = converter.convert(output_dir, output)
        assert len(output_files) == 1
        assert output_files[0].is_file()
        validation_process = run(
            ["verapdf", "-f", f"{pdfa_ver}b", "--format", "json", str(output_files[0])],
            capture_output=True,
            encoding="utf-8",
        )
        validation = loads(validation_process.stdout)
        assert validation["report"]["batchSummary"]["validationSummary"]["compliantPdfaCount"] == 1
