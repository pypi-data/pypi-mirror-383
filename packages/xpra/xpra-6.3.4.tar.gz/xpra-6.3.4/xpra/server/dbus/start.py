#!/usr/bin/env python3
# This file is part of Xpra.
# Copyright (C) 2016 Antoine Martin <antoine@xpra.org>
# Xpra is released under the terms of the GNU GPL v2, or, at your option, any
# later version. See the file COPYING for details.

import os
import shlex
from subprocess import Popen, PIPE

from xpra.os_util import POSIX
from xpra.scripts.config import FALSE_OPTIONS, TRUE_OPTIONS
from xpra.log import Logger

log = Logger("dbus")


def start_dbus(dbus_launch) -> tuple[int, dict]:
    if not dbus_launch or dbus_launch.lower() in FALSE_OPTIONS:
        log("start_dbus(%s) disabled", dbus_launch)
        return 0, {}
    if dbus_launch.lower() in TRUE_OPTIONS:
        log.warn(f"Warning: invalid dbus-launch command {dbus_launch!r}")
        return 0, {}
    bus_address = os.environ.get("DBUS_SESSION_BUS_ADDRESS")
    log("dbus_launch=%r, current DBUS_SESSION_BUS_ADDRESS=%s", dbus_launch, bus_address)
    if bus_address:
        log.warn("Warning: found an existing dbus instance:")
        log.warn(" DBUS_SESSION_BUS_ADDRESS=%s", bus_address)
    assert POSIX
    try:
        env = {k: v for k, v in os.environ.items() if k in (
            "PATH",
            "SSH_CLIENT", "SSH_CONNECTION",
            "XDG_CURRENT_DESKTOP", "XDG_SESSION_TYPE", "XDG_RUNTIME_DIR",
            "SHELL", "LANG", "USER", "LOGNAME", "HOME",
            "DISPLAY", "XAUTHORITY", "CKCON_X11_DISPLAY",
            "NO_AT_BRIDGE",
        )}
        cmd = shlex.split(dbus_launch)
        log("start_dbus(%s) env=%s", dbus_launch, env)
        proc = Popen(cmd, stdin=PIPE, stdout=PIPE, env=env, start_new_session=True, universal_newlines=True)
        out = proc.communicate()[0]
        assert proc.poll() == 0, "exit code is %s" % proc.poll()
        # parse and add to global env:
        dbus_env: dict[str, str] = {}
        log("out(%s)=%r", cmd, out)
        for line in out.splitlines():
            if line.startswith("export "):
                continue
            sep = "="
            if line.startswith("setenv "):
                line = line[len("setenv "):]
                sep = " "
            if line.startswith("set "):
                line = line[len("set "):]
            parts = line.split(sep, 1)
            if len(parts) != 2:
                continue
            k, v = parts
            if v.startswith("'") and v.endswith("';"):
                v = v[1:-2]
            elif v.endswith(";"):
                v = v[:-1]
            dbus_env[k] = v
        dbus_pid = int(dbus_env.get("DBUS_SESSION_BUS_PID", 0))
        log("dbus_pid=%i, dbus-env=%s", dbus_pid, dbus_env)
        return dbus_pid, dbus_env
    except Exception as e:
        log("start_dbus(%s)", dbus_launch, exc_info=True)
        log.error("dbus-launch failed to start using command '%s':\n" % dbus_launch)
        log.error(" %s\n" % e)
        return 0, {}
