# This file is part of Xpra.
# Copyright (C) 2017 Antoine Martin <antoine@xpra.org>
# Xpra is released under the terms of the GNU GPL v2, or, at your option, any
# later version. See the file COPYING for details.

import struct

from xpra.net.rfb.const import RFBEncoding
from xpra.codecs.rgb_transform import rgb_reformat
from xpra.codecs.pillow.encoder import encode
from xpra.util.objects import typedict
from xpra.util.str_fn import hexstr
from xpra.log import Logger

log = Logger("rfb")

PILLOW_OPTIONS = typedict({"alpha": False})


def pillow_encode(encoding, img):
    return encode(encoding, img, PILLOW_OPTIONS)[1].data


def make_header(encoding, x, y, w, h):
    fbupdate = struct.pack(b"!BBH", 0, 0, 1)
    rect = struct.pack(b"!HHHHi", x, y, w, h, encoding)
    return fbupdate + rect


def rgb222_encode(window, x, y, w, h):
    img = window.get_image(x, y, w, h)
    window.acknowledge_changes()
    header = make_header(RFBEncoding.RAW, x, y, w, h)
    if img.get_pixel_format() != "BGRX":
        log.warn("Warning: cannot convert %s to rgb222", img.get_pixel_format())
        return []
    pixels = img.get_pixels()
    from xpra.codecs.argb.argb import bgra_to_rgb222  # pylint: disable=no-name-in-module
    data = bgra_to_rgb222(pixels)
    return [header, data]


def raw_encode(window, x, y, w, h):
    img = window.get_image(x, y, w, h)
    window.acknowledge_changes()
    header = make_header(RFBEncoding.RAW, x, y, w, h)
    return [header, raw_pixels(img)]


def raw_pixels(img):
    if not img:
        return []
    w = img.get_width()
    h = img.get_height()
    Bpp = len(img.get_pixel_format())  # ie: BGRX -> 4
    if img.get_rowstride() != w * Bpp:
        img.restride(w * Bpp)
    pixels = img.get_pixels()
    assert len(pixels) >= Bpp * w * h, "expected %i pixels for %ix%i-%i but got %i" % (
        Bpp * w * h, w, h, Bpp, len(pixels))
    return pixels[:Bpp * w * h]


def zlib_encode(window, x, y, w, h):
    img = window.get_image(x, y, w, h)
    window.acknowledge_changes()
    if not img:
        return []
    pixels = raw_pixels(img)
    import zlib  # pylint: disable=import-outside-toplevel
    if isinstance(pixels, memoryview):
        pixels = pixels.tobytes()
    data = zlib.compress(pixels, 1)
    log("zlib compressed %i down to %i", len(pixels), len(data))
    header = make_header(RFBEncoding.ZLIB, x, y, w, h) + struct.pack(b"!I", len(data))
    return [header, data]


def tight_encode(window, x, y, w, h, quality=0):
    img = window.get_image(x, y, w, h)
    window.acknowledge_changes()
    if not img:
        return []
    if quality == 10:
        # Fill Compression
        header = make_header(RFBEncoding.TIGHT, x, y, w, h)
        header += struct.pack(b"!B", 0x80)
        pixel_format = img.get_pixel_format()
        log.warn("fill compression of %s", pixel_format)
        if not rgb_reformat(img, ("RGB",), False):
            log.error("Error: cannot convert %s to RGB", pixel_format)
        return [header, raw_pixels(img)]
    # try jpeg:
    data = pillow_encode("jpeg", img)
    header = tight_header(RFBEncoding.TIGHT, x, y, w, h, 0x90, len(data))
    return [header, data]


def tight_header(encoding, x, y, w, h, control, length):
    header = make_header(encoding, x, y, w, h)
    header += struct.pack(b"!B", control)
    # the length header is in a weird format:
    if length < 128:
        header += struct.pack(b"!B", length)
    elif length < 16383:
        header += struct.pack(b"!BB", 0x80 + (length & 0x7F), length >> 7)
    else:
        assert length < 4194303
        header += struct.pack(b"!BBB", 0x80 + (length & 0x7F), 0x80 + ((length >> 7) & 0x7F), length >> 14)
    log("tight header for %i bytes %s", length, hexstr(header))
    return header


def tight_png(window, x, y, w, h):
    img = window.get_image(x, y, w, h)
    window.acknowledge_changes()
    if not img:
        return []
    data = pillow_encode("png", img)
    header = tight_header(RFBEncoding.TIGHT_PNG, x, y, w, h, 0x80 + 0x20, len(data))
    return [header, data]
