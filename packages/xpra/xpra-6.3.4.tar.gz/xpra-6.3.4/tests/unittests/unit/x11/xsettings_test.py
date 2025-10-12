#!/usr/bin/env python3
# This file is part of Xpra.
# Copyright (C) 2020 Antoine Martin <antoine@xpra.org>
# Xpra is released under the terms of the GNU GPL v2, or, at your option, any
# later version. See the file COPYING for details.

import os
import struct
import unittest
import binascii

from xpra.util.env import OSEnvContext
from unit.test_util import LoggerSilencer


class XSettingsTest(unittest.TestCase):

    def test_xsettings(self):
        from xpra.x11.xsettings_prop import (
            xsettings_to_bytes, bytes_to_xsettings,
            get_local_byteorder,
            XSettingsType,
            )
        for v in (None, 10, "", (), [], (1, 2, 3), [1, ]):
            try:
                xsettings_to_bytes(v)
            except (ValueError, TypeError):
                continue
            else:
                raise RuntimeError(f"should not be able to parse {v!r}")

        for v in (None, 10, struct.pack(b"=BBBBII", 0, 0, 0, 0, 100, 2)):
            #setting_type, _, name_len = struct.unpack(b"=BBH", d[pos:pos + 4])
            try:
                assert not bytes_to_xsettings(v)
            except (ValueError, TypeError):
                continue
            else:
                raise RuntimeError(f"should not be able to parse {v!r}")

        for DEBUG_XSETTINGS in (True, False):
            with OSEnvContext():
                os.environ["XPRA_XSETTINGS_DEBUG"] = str(int(DEBUG_XSETTINGS))
                serial = 1
                data = b""
                l = len(data)
                v = struct.pack(b"=BBBBII", get_local_byteorder(), 0, 0, 0, serial, l)+data+b"\0"
                v1 = bytes_to_xsettings(v)
                assert v
                # get from cache:
                v2 = bytes_to_xsettings(v)
                assert v1==v2

                # test all types, set then get:
                # setting_type, prop_name, value, last_change_serial = setting
                settings = (
                    (XSettingsType.Integer, "int1", 1, 0),
                    (XSettingsType.String, "str1", "1", 0),
                    (XSettingsType.Color, "color1", (128, 128, 64, 32), 0),
                    )
                serial = 2
                data = xsettings_to_bytes((serial, settings))
                assert data
                # parse it back:
                v = bytes_to_xsettings(data)
                rserial, rsettings = v
                assert rserial==serial
                assert len(rsettings)==len(settings)
        from xpra.x11 import xsettings_prop
        with LoggerSilencer(xsettings_prop):
            # test error handling:
            for settings in (
                (
                    # invalid color causes exception
                    (XSettingsType.Color, "bad-color", (128, ), 0),
                ),
                (
                    # invalid setting type is skipped with an error message:
                    (255, "invalid-setting-type", 0, 0),
                ),
            ):
                serial = 3
                data = xsettings_to_bytes((serial, settings))
                assert data
                v = bytes_to_xsettings(data)
                rserial, rsettings = v
                assert rserial==serial
                assert len(rsettings)==0
            # parsing an invalid data type (9) should fail:
            hexdata = b"000000000200000001000000090004007374723100000000010000003100000000"
            data = binascii.unhexlify(hexdata)
            v = bytes_to_xsettings(data)
            rserial, rsettings = v
            assert len(rsettings)==0


def main():
    #can only work with an X11 server
    from xpra.os_util import OSX, POSIX
    if POSIX and not OSX:
        unittest.main()

if __name__ == '__main__':
    main()
