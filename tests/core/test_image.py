# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
from pathlib import Path

import pytest
from PIL import Image
from PIL.Image import Image as PillowImage

from convertool.core.image import img2tif
from convertool.exceptions import ImageError

# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------


def raise_except(*args, **kwargs):
    raise Exception("Bad error")


class TestImage:
    def test_valid_input(self, test_jpg, test_out):
        img2tif(test_jpg, test_out)
        test_tif: Path = test_out / "test.tif"
        assert test_tif.is_file()
        assert test_tif.stat().st_size > 1000000

    def test_load_error(self, test_jpg, test_out, monkeypatch):
        monkeypatch.setattr(Image, "open", raise_except)
        err_match = r"Failed to load .* as an image with error: Bad error"
        with pytest.raises(ImageError, match=err_match):
            img2tif(test_jpg, test_out)

    def test_save_error(self, test_jpg, test_out, monkeypatch):
        monkeypatch.setattr(PillowImage, "save", raise_except)
        err_match = r"Failed to save .* as TIF with error: Bad error"
        with pytest.raises(ImageError, match=err_match):
            img2tif(test_jpg, test_out)
