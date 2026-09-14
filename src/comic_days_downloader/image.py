import math
import os
from io import BytesIO

import requests
from PIL import Image

from comic_days_downloader.scraper import USER_AGENT


def descramble_page(page_number: int, image_data: dict, output_dir: str) -> str:
    """Download one page image and undo comic-days.com's tile-scramble, saving a PNG.

    Returns the path to the saved file.
    """

    print(f"Processing page {page_number:02d}...")

    src = image_data["src"]

    page_width = int(image_data["width"])
    page_height = int(image_data["height"])

    spacing_width = math.floor(page_width / 32) * 8
    spacing_height = math.floor(page_height / 32) * 8

    if spacing_width <= 0 or spacing_height <= 0:
        raise RuntimeError(
            f"Invalid spacing dimensions for page {page_number}: "
            f"{spacing_width}x{spacing_height}"
        )

    response = requests.get(src, timeout=30, headers={"User-Agent": USER_AGENT})
    response.raise_for_status()

    mixed_image = Image.open(BytesIO(response.content)).convert("RGBA")

    new_image = Image.new("RGBA", (page_width, page_height))

    # Rearrange scrambled image tiles back into place.
    image_x = 0

    while image_x + spacing_width <= page_width:

        image_y = (image_x // spacing_width) * spacing_height + spacing_height

        while image_y + spacing_height <= page_height:

            old_x, old_y = image_x, image_y

            partial_image_old = mixed_image.crop(
                (old_x, old_y, old_x + spacing_width, old_y + spacing_height)
            )

            new_x = (image_y // spacing_height) * spacing_width
            new_y = (image_x // spacing_width) * spacing_height

            partial_image_new = mixed_image.crop(
                (new_x, new_y, new_x + spacing_width, new_y + spacing_height)
            )

            new_image.alpha_composite(partial_image_new, (image_x, image_y))
            new_image.alpha_composite(partial_image_old, (new_x, new_y))

            image_y += spacing_height

        image_x += spacing_width

    # Copy the 4 middle-line blocks, which are never scrambled.
    for middle_line in range(4):

        middle_line_x = middle_line * spacing_width
        middle_line_y = middle_line * spacing_height

        partial_middle = mixed_image.crop(
            (
                middle_line_x,
                middle_line_y,
                middle_line_x + spacing_width,
                middle_line_y + spacing_height,
            )
        )

        new_image.alpha_composite(partial_middle, (middle_line_x, middle_line_y))

    file_path = os.path.join(output_dir, f"{page_number}.png")
    new_image.save(file_path, "PNG")

    print(f"Page {page_number:02d} done!")

    return file_path
