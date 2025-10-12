#!/usr/bin/env python3
# This file is part of Xpra.
# Copyright (C) 2020 Antoine Martin <antoine@xpra.org>
# Xpra is released under the terms of the GNU GPL v2, or, at your option, any
# later version. See the file COPYING for details.

import unittest

from xpra.os_util import OSX, POSIX
from unit.test_util import silence_warn


class TestX11Keyboard(unittest.TestCase):

    def test_sanitize(self):
        from xpra.x11.models import size_hints_util
        MAX_ASPECT = size_hints_util.MAX_ASPECT
        with silence_warn(size_hints_util):
            INTPAIRS = (0, "foo", (1,))
            for attr, values in {
                "min-aspect"    : (0, -1, MAX_ASPECT, "foo"),
                "max-aspect"    : (0, -1, MAX_ASPECT, "foo"),
                "minimum-aspect-ratio"  : ((0, 1), (0, 0), (MAX_ASPECT, 1), "foo"),
                "maximum-aspect-ratio"  : ((0, 1), (0, 0), (MAX_ASPECT, 1), "foo"),
                "maximum-size"  : INTPAIRS,
                "minimum-size"  : INTPAIRS,
                "base-size"     : INTPAIRS,
                "increment"     : INTPAIRS,
                }.items():
                for value in values:
                    hints = { attr : value }
                    size_hints_util.sanitize_size_hints(hints)
                    assert attr not in hints, "%s=%s should have been removed" % (attr, value)
            hints = {
                "minimum-size"  : (-1, -1),
                "maximum-size"  : (-1, -1),
                }
            size_hints_util.sanitize_size_hints(hints)
            assert hints.get("minimum-size") is None
            assert hints.get("maximum-size") is None
            for mins, maxs in ((100, 50), (512, 128), (512, 256),):
                hints = {
                    "minimum-size"  : (mins, mins),
                    "maximum-size"  : (maxs, maxs),
                    }
                size_hints_util.sanitize_size_hints(hints)
                assert hints.get("minimum-size")==hints.get("maximum-size")

def main():
    #can only work with an X11 server
    if POSIX and not OSX:
        unittest.main()

if __name__ == '__main__':
    main()
