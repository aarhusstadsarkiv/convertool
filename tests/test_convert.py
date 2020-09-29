# from pathlib import Path
# from unittest.mock import patch
# import pytest
# from convertool.convert import calc_timeout, check_errors, convert_files
# from convertool.exceptions import ConversionError
# from convertool.internals import FileConv
# class TestAuxFunctions:
#     def test_calc_timeout(self):
#         assert calc_timeout(Path("bogus"), 0) == 0
#     def test_check_errors(self):
#         assert check_errors(err_count=0, max_errs=1) == ""
#         errs = 3
#         max_errs = 2
#         assert (
#             f"Error count {errs} is higher than threshold of {max_errs}"
#             in check_errors(err_count=errs, max_errs=max_errs)
#         )
# class TestConvertFiles:
#     def test_with_valid_input(self, file_handler, caplog):
#         out, file = file_handler
#         file_conv = FileConv(
#             files=[{"path": file}], convert_to="odt", out_dir=out
#         )
#         convert_files("libre", file_conv)
#         assert "Started conversion of 1 files" in caplog.text
#         assert "Finished conversion of 1 files with 0 issues" in caplog.text
#     def test_convert_to(self, file_handler, caplog):
#         out, file = file_handler
#         convert_to = "bogus"
#         file_conv = FileConv(
#             files=[{"path": file}], convert_to=convert_to, out_dir=out
#         )
#         with pytest.raises(ConversionError):
#             convert_files("libre", file_conv)
#         assert f"Output to {convert_to} is not supported!" in caplog.text
# def test_parents(self, file_handler, caplog):
#     out, file = file_handler
#     # Our test file does indeed have two parents, things go well
#     file_conv = FileConv(
#         files=[{"path": file}], convert_to=convert_to, out_dir=out
#     )
#     convert_files("libre", [file], out, "pdf", parents=2)
#     assert "Started conversion of 1 files" in caplog.text
#     assert "Finished conversion of 1 files with 0 issues" in caplog.text
#     # It definitely does not have sys.maxsize parents though
#     with pytest.raises(ConversionError):
#         convert_files("libre", [file], out, "pdf", parents=sys.maxsize)
#     assert (
#         f"Parent index {sys.maxsize} out of range for {file}"
#         in caplog.text
#     )
#     def test_libre_convert(self, file_handler, caplog):
#         out, file = file_handler
#         file_conv = FileConv(
#             files=[{"path": file}], convert_to="pdf", out_dir=out
#         )
#         with patch("convertool.convert.calc_timeout", return_value=0):
#             convert_files("libre", file_conv)
#         assert (
#             f"LibreConvert of {file} timed out after 0 seconds" in
# caplog.text
#         )
#     def test_context_convert(self, pdf_file_handler, caplog):
#         out, file = pdf_file_handler
#         file_conv = FileConv(
#             files=[{"path": file}], convert_to="tiff", out_dir=out
#         )
#         convert_files("context", file_conv)
#         assert "Started conversion of 1 files" in caplog.text
#         assert "Finished conversion of 1 files with 0 issues" in caplog.text
