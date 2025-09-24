from pathlib import Path

from acacore.siegfried import Siegfried

from convertool.converters.base import dummy_base_file
from convertool.converters.converter_pdf import ConverterPDF


# noinspection DuplicatedCode
def test_pdf_to_pdfa(test_files: dict[str, Path], output_dir: Path, siegfried: Siegfried):
    file = dummy_base_file(test_files["pdf-to-pdfa.pdf"], test_files["pdf-to-pdfa.pdf"].parent)
    converter = ConverterPDF(file)

    for pdfa_ver in (1, 2, 3):
        output: str = f"pdfa-{pdfa_ver}"
        print(output)
        output_files = converter.convert(output_dir, output)
        assert len(output_files) == 1
        assert output_files[0].is_file()
        match = siegfried.identify(output_files[0]).files[0]
        assert match.best_match().mime == "application/pdf"
