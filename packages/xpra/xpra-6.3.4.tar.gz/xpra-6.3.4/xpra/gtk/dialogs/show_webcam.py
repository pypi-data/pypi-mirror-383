#!/usr/bin/env python3
# This file is part of Xpra.
# Copyright (C) 2016 Antoine Martin <antoine@xpra.org>
# Xpra is released under the terms of the GNU GPL v2, or, at your option, any
# later version. See the file COPYING for details.


import sys


def main():
    from xpra.platform import program_context, command_error
    from xpra.platform.gui import init, set_default_icon
    with program_context("Webcam", "Webcam"):
        from xpra.log import Logger, consume_verbose_argv
        consume_verbose_argv(sys.argv, "webcam")
        log = Logger("webcam")
        set_default_icon("webcam.png")
        init()

        log("importing opencv")
        try:
            import cv2
        except ImportError as e:
            command_error("Error: no opencv support module: %s" % e)
            return 1
        log("cv2=%s", cv2)
        device = 0
        if len(sys.argv) == 2:
            try:
                device = int(sys.argv[1])
            except ValueError:
                command_error("Warning: failed to parse value as a device number: '%s'" % sys.argv[1])
        log("opening %s with device=%s", cv2.VideoCapture, device)  # @UndefinedVariable
        try:
            cap = cv2.VideoCapture(device)  # @UndefinedVariable
        except Exception as e:
            command_error(f"Error: failed to capture video using device {device}:\n{e}")
            return 1
        log.info("capture device for %i: %s", device, cap)
        while True:
            ret, frame = cap.read()
            if not ret:
                command_error("Error: frame capture failed using device %s" % device)
                return 1
            cv2.imshow('frame', frame)  # @UndefinedVariable
            if cv2.waitKey(10) & 0xFF in (ord('q'), 27):  # @UndefinedVariable
                break
        cap.release()
        cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    v = main()
    sys.exit(v)
