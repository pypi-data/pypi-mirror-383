#!/usr/bin/env python3
# This file is part of Xpra.
# Copyright (C) 2018 Antoine Martin <antoine@xpra.org>
# Xpra is released under the terms of the GNU GPL v2, or, at your option, any
# later version. See the file COPYING for details.

import tempfile
import unittest

from xpra.util.objects import AdHocStruct
from unit.server.mixins.servermixintest_util import ServerMixinTest


class MMAPMixinTest(ServerMixinTest):

    def _test_mmap(self, opts):
        from xpra.server.mixins.mmap import MMAP_Server
        self._test_mixin_class(MMAP_Server, opts)
        assert self.mixin.get_info().get("mmap", {}).get("supported") is True

    def test_mmap_on(self):
        opts = AdHocStruct()
        opts.mmap = "on"
        self._test_mmap(opts)

    def test_mmap_path(self):
        opts = AdHocStruct()
        opts.mmap = tempfile.gettempdir()+"/mmap-test-file"
        self._test_mmap(opts)

def main():
    unittest.main()


if __name__ == '__main__':
    main()
