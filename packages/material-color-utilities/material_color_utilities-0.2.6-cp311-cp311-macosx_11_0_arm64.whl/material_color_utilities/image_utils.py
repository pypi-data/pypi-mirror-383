import numpy as np
from PIL.Image import Image

from material_color_utilities._core import (
    CustomColor,
    Theme,
    Variant,
    prominent_colors_from_array,
    prominent_colors_from_array_argb,
    theme_from_array,
)


def image_to_argb(img: Image) -> np.ndarray:
    """Converts an image to ARGB flattened array with a length of 128 * 128 = 16384.

    Args:
        img: The input image to be converted.

    Returns:
        A 1D numpy array representing the image in ARGB format.
    """
    # Convert the image to 128x128 RGBA
    img = img.convert("RGBA")
    img.thumbnail((128, 128))

    # Extract channels: Alpha, Red, Green, Blue
    rgba_array = np.array(img)
    alpha = rgba_array[:, :, 3].astype(np.uint32) << 24
    red = rgba_array[:, :, 0].astype(np.uint32) << 16
    green = rgba_array[:, :, 1].astype(np.uint32) << 8
    blue = rgba_array[:, :, 2].astype(np.uint32)

    # Combine into ARGB format
    return (alpha | red | green | blue).ravel()


def prominent_colors_from_image_argb(img: Image, max_colors: int = 128) -> list[int]:
    """
    Extracts prominent ARGB colors from an image.

    The image is resized to 128x128 for performance before processing.
    More info:
        https://github.com/material-foundation/material-color-utilities/blob/main/concepts/color_extraction.md

    Args:
        img: The input image from which to extract colors.
        max_colors: A limit on the number of colors returned by the quantizer.
            Does not directly determine how many colors are returned, a reasonable default is 128.

    Returns:
        A list of prominent colors in ARGB format.
    """
    return prominent_colors_from_array_argb(image_to_argb(img), max_colors)


def prominent_colors_from_image(img: Image, max_colors: int = 128) -> list[str]:
    """
    Extracts prominent hex colors from an image.

    The image is resized to 128x128 for performance before processing.
    More info:
        https://github.com/material-foundation/material-color-utilities/blob/main/concepts/color_extraction.md

    Args:
        img: The input image from which to extract colors.
        max_colors: A limit on the number of colors returned by the quantizer.
            Does not directly determine how many colors are returned, a reasonable default is 128.

    Returns:
        A list of prominent colors in hex format.
    """
    return prominent_colors_from_array(image_to_argb(img), max_colors)


def theme_from_image(
    img: Image,
    contrast: float = 3,
    variant: Variant = Variant.VIBRANT,
    custom_colors: list[CustomColor] | None = None,
) -> Theme:
    """
    Generates a theme from an image, considering contrast, variant, and custom colors.

    The image is resized to 128x128 for performance before processing.

    Args:
        img: The input image used to generate the theme.
        contrast: The contrast level maintain between texts and their backgrounds.
        variant: Each variant is a set of design decisions on the assignment of color values from tonal palettes to color roles.
        custom_colors: A list of custom colors to be included in the theme.

    Returns:
        A theme generated from the image.
    """
    if custom_colors is None:
        custom_colors = []
    return theme_from_array(image_to_argb(img), contrast, variant, custom_colors)
