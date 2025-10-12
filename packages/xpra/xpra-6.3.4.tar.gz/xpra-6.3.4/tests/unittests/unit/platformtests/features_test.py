#!/usr/bin/env python3
# This file is part of Xpra.
# Copyright (C) 2020 Antoine Martin <antoine@xpra.org>
# Xpra is released under the terms of the GNU GPL v2, or, at your option, any
# later version. See the file COPYING for details.

import unittest

from xpra.platform.features import main as features_main

class FeaturesTest(unittest.TestCase):

    def test_main(self):
        from xpra.util import str_fn
        def noop(*_args):
            pass
        str_fn.print_nested_dict = noop
        features_main()

def main():
    unittest.main()

if __name__ == '__main__':
    main()
