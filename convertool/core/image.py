# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
from pathlib import Path

from PIL import Image
from PIL.Image import Image as PillowImage

from convertool.exceptions import ImageError

# -----------------------------------------------------------------------------
# Image conversion
# -----------------------------------------------------------------------------


def img2tif(img_file: Path, out_dir: Path) -> None:
    img_out: Path = out_dir / img_file.name
    img_out = img_out.with_suffix(".tif")

    try:
        im: PillowImage = Image.open(img_file)
    except Exception as e:
        raise ImageError(
            f"Failed to load {img_file} as an image with error: {e}"
        )
    else:
        im.load()
        try:
            im.save(str(img_out), compression="tiff_lzw")
        except Exception as e:
            raise ImageError(
                f"Failed to save {img_file} as TIF with error: {e}"
            )
