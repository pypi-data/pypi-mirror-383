#!/usr/bin/env python3
# This file is part of Xpra.
# Copyright (C) 2016 Antoine Martin <antoine@xpra.org>
# Xpra is released under the terms of the GNU GPL v2, or, at your option, any
# later version. See the file COPYING for details.

import os
import time
import tempfile
import subprocess

from unit.process_test_util import ProcessTestUtil
from xpra.util.env import envint
from xpra.os_util import WIN32
from xpra.util.io import pollwait
from xpra.exit_codes import exit_str
from xpra.platform.dotxpra import DotXpra, DISPLAY_PREFIX
from xpra.log import Logger

log = Logger("test")

SERVER_TIMEOUT = envint("XPRA_TEST_SERVER_TIMEOUT", 8)
STOP_WAIT_TIMEOUT = envint("XPRA_STOP_WAIT_TIMEOUT", 20)


def log_gap(N=10) -> None:
    for _ in range(N):
        log("")


def estr(r) -> str:
    return exit_str(r)


class ServerTestUtil(ProcessTestUtil):

    @classmethod
    def displays(cls):
        return cls.dotxpra.displays()

    @classmethod
    def find_free_display(cls):
        dno = cls.find_free_display_no(cls.displays())
        return "%s%i" % (DISPLAY_PREFIX, dno)

    @classmethod
    def setUpClass(cls):
        ProcessTestUtil.setUpClass()
        tmpdir = tempfile.gettempdir()
        cls.dotxpra = DotXpra(tmpdir, [tmpdir])
        cls.default_xpra_args: list[str] = ["--speaker=no", "--microphone=no"]
        if not WIN32:
            cls.default_xpra_args += ["--systemd-run=no", "--pulseaudio=no"]
            for x in cls.dotxpra._sockdirs:
                cls.default_xpra_args += ["--socket-dirs=%s" % x]
        cls.existing_displays = cls.displays()

    @classmethod
    def tearDownClass(cls):
        ProcessTestUtil.tearDownClass()
        displays = set(cls.displays())
        new_displays = displays - set(cls.existing_displays)
        if new_displays:
            for x in list(new_displays):
                log("stopping display %s" % x)
                try:
                    cmd = cls.get_xpra_cmd() + ["stop", x]
                    proc = subprocess.Popen(cmd)
                    proc.communicate(None)
                except Exception:
                    log.error("failed to cleanup display '%s'", x, exc_info=True)
        if cls.xauthority_temp:
            try:
                os.unlink(cls.xauthority_temp.name)
            except OSError as e:
                log.error("Error deleting '%s': %s", cls.xauthority_temp.name, e)
            cls.xauthority_temp = None

    def setUp(self):
        ProcessTestUtil.setUp(self)
        xpra_list = self.run_xpra(["list"])
        assert pollwait(xpra_list, 15) is not None, "xpra list returned %s" % xpra_list.poll()

    def run_xpra(self, xpra_args, **kwargs):
        cmd = self.get_xpra_cmd() + list(xpra_args)
        return self.run_command(cmd, **kwargs)

    @classmethod
    def get_xpra_cmd(cls) -> list[str]:
        return ProcessTestUtil.get_xpra_cmd() + cls.default_xpra_args

    def run_server(self, *args):
        display = self.find_free_display()
        server = self.check_server("start", display, *args)
        server.display = display
        return server

    def check_fast_start_server(self, display: str, *args):
        defaults: dict[str, str] = dict((k, "no") for k in (
            "av-sync", "remote-logging",
            "windows",
            "mdns",
            "rfb-upgrade", "ssh-upgrade",
            "speaker", "microphone", "audio",
            "systemd-run", "start-via-proxy",
            "splash", "printing", "opengl",
            "webcam", "bell", "system-tray", "notifications",
            "clipboard", "start-new-commands",
        ))
        defaults.update({
            "video-encoders": "none",
            "csc-modules": "none",
            "video-decoders": "none",
            "encodings": "rgb",
        })
        args = [f"--{k}={v}" for k, v in defaults.items()] + list(args)
        return self.check_server("start", display, *args)

    def check_start_server(self, display: str, *args):
        return self.check_server("start", display, *args)

    def check_server(self, subcommand: str, display: str, *args):
        cmd = [subcommand]
        if display:
            cmd.append(display)
        if not WIN32:
            cmd += ["--no-daemon"]
        cmd += list(args)
        server_proc = self.run_xpra(cmd)
        if pollwait(server_proc, SERVER_TIMEOUT) is not None:
            self.show_proc_error(server_proc, "server failed to start")
        if display:
            #wait until the socket shows up:
            live: list[str] = []
            for _ in range(20):
                live = self.dotxpra.displays()
                if display in live:
                    break
                time.sleep(1)
            if server_proc.poll() is not None:
                self.show_proc_error(server_proc, "server terminated")
            assert display in live, "server display '%s' not found in live displays %s" % (display, live)
            #then wait a little before using it:
            time.sleep(5)
        #query it:
        version = None
        r = 0
        for _ in range(20):
            if version is None:
                args = ["version"]
                if display:
                    args.append(display)
                version = self.run_xpra(args)
            r = pollwait(version, 1)
            log("version for %s returned %s", display, r)
            if r is not None:
                if r == 1:
                    #re-run it
                    version = None
                    continue
                break
            time.sleep(1)
        if r != 0:
            self.show_proc_error(version, "version check failed for %s, returned %s" % (
                display, exit_str(r)))
        return server_proc

    def stop_server(self, server_proc, subcommand: str, *connect_args) -> None:
        assert subcommand in ("stop", "exit"), "invalid stop subcommand '%s'" % subcommand
        if server_proc.poll() is not None:
            raise Exception("cannot stop server, it has already exited, returncode=%i" % server_proc.poll())
        cmd = [subcommand] + list(connect_args)
        stopit = self.run_xpra(cmd)
        log("stop_server%s stopit=%s", (server_proc, subcommand, connect_args), stopit)
        if pollwait(stopit, STOP_WAIT_TIMEOUT) is None:
            log("failed to '%s' server: %s", subcommand, getattr(server_proc, "command", server_proc))
            self.show_proc_pipes(server_proc)
            self.show_proc_error(stopit, "%s server error" % subcommand)
            raise Exception("server process %s failed to '%s'" % (server_proc, subcommand))

    def check_stop_server(self, server_proc, subcommand="stop", display=":99999") -> None:
        log("check_stop_server%s", (server_proc, subcommand, display))
        self.stop_server(server_proc, subcommand, display)
        if not display:
            return
        for _ in range(10):
            displays = self.dotxpra.displays()
            log("check_stop_server: display=%s, displays=%s", display, displays)
            if display not in displays:
                return
            time.sleep(1)
        raise Exception(
            "server socket for display %s should have been removed, but it is still found in %s" % (display, displays))

    @classmethod
    def get_server_info(cls, display: str):
        #wait for client to own the clipboard:
        cmd = cls.get_xpra_cmd() + ["info", display]
        out = cls.get_command_output(cmd)
        #print("info=%s" % (out,))
        info = {}
        for line in out.decode().splitlines():
            if line.find("=") > 0:
                k, v = line.split("=", 1)
                info[k] = v
        #print("info=%s" % (info,))
        return info
