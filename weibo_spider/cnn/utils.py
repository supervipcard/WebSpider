import numpy as np
from PIL import Image


def resize_image(image, in_shape, proc_img=True):
    iw, ih = image.size
    h, w = in_shape[0], in_shape[1]

    # resize image
    scale = min(w / iw, h / ih)
    nw = int(iw * scale)
    nh = int(ih * scale)
    dx = (w - nw) // 2
    dy = (h - nh) // 2
    image_data = 0
    if proc_img:
        image = image.resize((nw, nh), Image.BICUBIC)
        new_image = Image.new('RGB', (w, h), (128, 128, 128))
        new_image.paste(image, (dx, dy))
        image_data = np.array(new_image) / 255.

    return image_data
