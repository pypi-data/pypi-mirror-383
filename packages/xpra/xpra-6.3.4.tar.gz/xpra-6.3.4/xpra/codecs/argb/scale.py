#!/usr/bin/env python3
# This file is part of Xpra.
# Copyright (C) 2021 Antoine Martin <antoine@xpra.org>
# Xpra is released under the terms of the GNU GPL v2, or, at your option, any
# later version. See the file COPYING for details.

from xpra.log import Logger
from xpra.codecs.image import ImageWrapper

log = Logger("encoding")

# more scaling functions can be added here later

RGB_SCALE_FORMATS = ("BGRX", "BGRA", "RGBA", "RGBX",)


def scale_image(image: ImageWrapper, width: int, height: int) -> ImageWrapper:
    rgb_format = image.get_pixel_format()
    if rgb_format in RGB_SCALE_FORMATS:
        try:
            from xpra.codecs.libyuv.converter import argb_scale  # pylint: disable=import-outside-toplevel
        except ImportError as e:
            log("cannot downscale: %s", e)
        else:
            return argb_scale(image, image.get_width(), image.get_height(), width, height)
    return image
