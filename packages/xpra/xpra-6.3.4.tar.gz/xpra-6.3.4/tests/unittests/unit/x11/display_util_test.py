#!/usr/bin/env python3
# This file is part of Xpra.
# Copyright (C) 2020 Antoine Martin <antoine@xpra.org>
# Xpra is released under the terms of the GNU GPL v2, or, at your option, any
# later version. See the file COPYING for details.

import os
import unittest

from unit.server_test_util import ServerTestUtil
from xpra.os_util import POSIX, OSX
from xpra.util.env import OSEnvContext


class TestDisplayUtil(ServerTestUtil):

    def test_display(self):
        from xpra.scripts.server import verify_gdk_display
        with OSEnvContext():
            os.environ["GDK_BACKEND"] = "x11"
            os.environ.pop("DISPLAY", None)
            for d in ("NOTADISPLAY", ""):
                if verify_gdk_display(d):
                    raise RuntimeError(f"{d!r} is not a valid display")

            display = self.find_free_display()
            xvfb = self.start_Xvfb(display)
            os.environ["DISPLAY"] = display
            from xpra.x11.bindings.posix_display_source import X11DisplayContext    #@UnresolvedImport
            with X11DisplayContext(display):
                verify_gdk_display(display)
            xvfb.terminate()


def main():
    #can only work with an X11 server
    if POSIX and not OSX:
        unittest.main()


if __name__ == '__main__':
    main()
