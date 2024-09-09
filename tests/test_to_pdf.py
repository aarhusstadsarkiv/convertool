from os import environ
from pathlib import Path

from acacore.models.file import File
from acacore.siegfried import Siegfried

from convertool.converters.converter_to_pdf import ConverterToPDF


# noinspection DuplicatedCode
def test_pdf_to_pdfa(test_files: dict[str, Path], reference_files: dict[str, Path], output_dir: Path):
    file = File.from_file(test_files["pdf-to-pdfa.pdf"], root=test_files["pdf-to-pdfa.pdf"].parent)
    converter = ConverterToPDF(file)
    siegfried = Siegfried(environ["SIEGFRIED_PATH"], "default.sig", environ["SIEGFRIED_HOME"])

    for pdfa_ver in (1, 2, 3):
        output: str = f"pdfa-{pdfa_ver}"
        print(output)
        output_files = converter.convert(output_dir, output)
        assert len(output_files) == 1
        assert output_files[0].is_file()
        match = siegfried.identify(output_files[0]).files[0]
        assert match.best_match().mime == "application/pdf"
