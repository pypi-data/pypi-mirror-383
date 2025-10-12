#!/usr/bin/env python3
# This file is part of Xpra.
# Copyright (C) 2018 Antoine Martin <antoine@xpra.org>
# Xpra is released under the terms of the GNU GPL v2, or, at your option, any
# later version. See the file COPYING for details.

import unittest

from xpra.util.objects import AdHocStruct
from unit.server.mixins.servermixintest_util import ServerMixinTest


class ServerMixinsTest(ServerMixinTest):

    def test_remotelogging(self):
        from xpra.server.mixins.logging import LoggingServer
        messages = []
        def newlogfn(*args):
            messages.append(args)
        def _LoggingServer():
            ls = LoggingServer()
            ls.do_log = newlogfn
            return ls
        opts = AdHocStruct()
        opts.remote_logging = "on"
        level = 20
        msg = "foo"
        packet = ["logging", level, msg]
        self._test_mixin_class(_LoggingServer, opts)
        self.handle_packet(packet)
        assert len(messages)==1

def main():
    unittest.main()


if __name__ == '__main__':
    main()
