# This file is part of Xpra.
# Copyright (C) 2010 Antoine Martin <antoine@xpra.org>
# Copyright (C) 2008 Nathaniel Smith <njs@pobox.com>
# Xpra is released under the terms of the GNU GPL v2, or, at your option, any
# later version. See the file COPYING for details.

from collections.abc import Sequence

from xpra.util.version import version_compat_check, parse_version
from xpra.util.io import get_util_logger
from xpra.util.str_fn import bytestostr
from xpra.util.objects import typedict
from xpra.client.base.stub_client_mixin import StubClientMixin
from xpra.exit_codes import ExitCode


def get_remote_lib_versions(c: typedict,
                            libs=(
                                "glib", "gobject", "gtk", "gdk", "cairo", "pango",
                                "sound.gst", "audio.gst",
                                "python",
                            )
                            ) -> dict:
    versions = {}
    for x in libs:
        v = c.get("%s.version" % x, None)
        if v is None:
            # fallback to structured access:
            d = c.get(x, None)
            if isinstance(d, dict):
                v = typedict(d).get("version", None)
            elif x.find(".") > 0:
                # recursive lookup:
                parts = x.split(".")
                while parts:
                    x = parts[0]
                    sub = c.get(x)
                    if sub and isinstance(sub, dict):
                        c = typedict(sub)
                        parts = parts[1:]
                    else:
                        break
                v = c.get("version", None)
        if v:
            if isinstance(v, (tuple, list)):
                v = tuple(v)
            else:
                v = parse_version(v)
            versions[x] = v
    return versions


class ServerInfoMixin(StubClientMixin):

    def __init__(self):  # pylint: disable=super-init-not-called
        super().__init__()
        self._remote_protocol = None
        self._remote_machine_id = None
        self._remote_uuid = None
        self._remote_version = None
        self._remote_revision = None
        self._remote_branch = ""
        self._remote_modifications = 0
        self._remote_commit = None
        self._remote_build_date = ""
        self._remote_build_time = ""
        self._remote_hostname = None
        self._remote_display = None
        self._remote_platform = None
        self._remote_platform_release = None
        self._remote_platform_platform = None
        self._remote_platform_linux_distribution = None
        self._remote_python_version = ""
        self._remote_lib_versions = {}
        self._remote_subcommands: Sequence[str] = ()
        self._remote_server_log = None
        self._remote_server_mode = ""

    def parse_server_capabilities(self, c: typedict) -> bool:
        p = self._protocol
        if p.TYPE == "rfb":
            # only the xpra protocol provides the server info
            return True
        self._remote_machine_id = c.strget("machine_id")
        self._remote_uuid = c.strget("uuid")
        self._remote_version = parse_version(c.strget("build.version", c.strget("version")))
        self._remote_revision = c.strget("build.revision", c.strget("revision"))
        mods = c.get("build.local_modifications")
        if mods and str(mods).find("dfsg") >= 0:  # pragma: no cover
            get_util_logger().warn("Warning: the xpra server is running a buggy Debian version")
            get_util_logger().warn(" those are usually out of date and unstable")
        else:
            self._remote_modifications = c.intget("build.local_modifications", 0)
        self._remote_commit = c.strget("build.commit")
        self._remote_branch = c.strget("build.branch")
        self._remote_build_date = c.strget("build.date")
        self._remote_build_time = c.strget("build.time")
        self._remote_hostname = c.strget("hostname")
        self._remote_display = c.strget("display")
        self._remote_platform = c.strget("platform")
        self._remote_platform_release = c.strget("platform.release")
        self._remote_platform_platform = c.strget("platform.platform")
        self._remote_python_version = c.strget("python.version")
        self._remote_subcommands = c.strtupleget("subcommands")
        self._remote_server_log = c.strget("server-log")
        self._remote_server_mode = c.strget("server.mode", "server")
        self._remote_lib_versions = get_remote_lib_versions(c)
        # linux distribution is a tuple of different types, ie: ('Linux Fedora' , 20, 'Heisenbug')
        pld = c.tupleget("platform.linux_distribution")
        if pld and len(pld) == 3:
            def san(v):
                if isinstance(v, int):
                    return v
                return bytestostr(v)

            self._remote_platform_linux_distribution = [san(x) for x in pld]
        verr = version_compat_check(self._remote_version)
        if verr is not None:
            vstr = ".".join(str(x) for x in (self._remote_version or ()))
            self.warn_and_quit(ExitCode.INCOMPATIBLE_VERSION, f"incompatible remote version {vstr!r}: {verr}")
            return False
        return True
