import io
import os

from urllib import request
from PIL import Image
from Spider import log
from Spider.config import *


def _getPilImg(url):
    img = request.urlopen(url).read()
    pil_image = Image.open(io.BytesIO(img)).convert("RGB")
    return pil_image


def saveThumbnail(url, imgname):
    try:
        pil_img = _getPilImg(url)
        width, height = pil_img.size
        box = ()
        if width >= height:
            scale = height / width
            if scale == thumbnail_standard:
                box = (0, 0, width, height)
            else:
                leng = height / 3 if scale < thumbnail_standard else width / 4
        else:
            scale = width / height
            leng = width / 4 if scale <= thumbnail_standard else height / 3

        if not box:
            x_padding = (width - leng * 4) / 2
            y_padding = (height - leng * 3) / 2
            box = (x_padding, y_padding, leng * 4 + x_padding, leng * 3 + y_padding)

        region = pil_img.crop(box)
        region.thumbnail(thumbnail_size, Image.ANTIALIAS)
        region.save(os.path.join(Thumbnail_DIR, imgname))
        return True
    except Exception as e:
        log.logMsg(log.LogType.error, "[FormThumbnail] %s" % repr(e))
    return False