from io import BytesIO

import numpy as np
from PIL import Image

from kiva.compat import piltostring

DEPTH_MAP = {'RGB': 3, 'RGBA': 4}


def img_data_to_img_array(data):
    """ Convert a buffer of encoded image data to a numpy array of pixels.
    """
    pil_img = Image.open(BytesIO(data))
    if pil_img.mode not in ('RGB', 'RGBA'):
        pil_img = pil_img.convert(mode='RGBA')

    depth = DEPTH_MAP[pil_img.mode]
    img = np.fromstring(piltostring(pil_img), np.uint8)
    return np.resize(img, (pil_img.size[1], pil_img.size[0], depth))
