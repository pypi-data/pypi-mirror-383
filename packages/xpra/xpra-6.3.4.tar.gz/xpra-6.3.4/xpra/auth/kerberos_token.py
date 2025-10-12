#!/usr/bin/env python3
# This file is part of Xpra.
# Copyright (C) 2018 Antoine Martin <antoine@xpra.org>
# Xpra is released under the terms of the GNU GPL v2, or, at your option, any
# later version. See the file COPYING for details.

import sys
from collections.abc import Sequence

from xpra.auth.sys_auth_base import SysAuthenticatorBase, xor, log
from xpra.auth.common import parse_uid, parse_gid
from xpra.net.digest import get_salt, get_digests, gendigest
from xpra.util.objects import typedict
from xpra.os_util import WIN32
from xpra.util.io import stderr_print


class Authenticator(SysAuthenticatorBase):
    CLIENT_USERNAME = True

    def __init__(self, **kwargs):
        self.service = kwargs.pop("service", "")
        self.uid = parse_uid(kwargs.pop("uid", None))
        self.gid = parse_gid(kwargs.pop("gid", None))
        kwargs["prompt"] = kwargs.pop("prompt", "kerberos token")
        super().__init__(**kwargs)
        log("kerberos-token auth: service=%r, username=%r", self.service, kwargs.get("username"))

    def get_uid(self) -> int:
        return self.uid

    def get_gid(self) -> int:
        return self.gid

    def __repr__(self):
        return "kerberos-token"

    def get_challenge(self, digests: Sequence[str]) -> tuple[bytes, str]:
        assert not self.challenge_sent
        self.req_challenge(digests, "kerberos")
        self.salt = get_salt()
        self.challenge_sent = True
        return self.salt, f"kerberos:{self.service}"

    def check_password(self, token: str) -> bool:
        log("check(%r)", token)
        assert self.challenge_sent
        try:
            if WIN32:
                import winkerberos as kerberos
            else:
                import kerberos  # @Reimport
        except ImportError as e:
            log("check(..)", exc_info=True)
            log.warn("Warning: cannot use kerberos token authentication:")
            log.warn(" %s", e)
            return False
        v, ctx = kerberos.authGSSServerInit(self.service)  # @UndefinedVariable
        if v != 1:
            log.error("Error: kerberos GSS server init failed for service '%s'", self.service)
            return False
        try:
            r = kerberos.authGSSServerStep(ctx, token)  # @UndefinedVariable
            log("kerberos auth server step result: %s", r == 1)
            if r != 1:
                return False
            targetname = kerberos.authGSSServerTargetName(ctx)  # @UndefinedVariable
            # response = kerberos.authGSSServerResponse(ctx)
            principal = kerberos.authGSSServerUserName(ctx)  # @UndefinedVariable
            # ie: user1@LOCALDOMAIN
            # maybe we should validate the realm?
            log("kerberos targetname=%s, principal=%s", targetname, principal)
            return True
        finally:
            kerberos.authGSSServerClean(ctx)  # @UndefinedVariable


def main(argv) -> int:
    # pylint: disable=import-outside-toplevel
    from xpra.platform import program_context
    with program_context("Kerberos-Token-Auth", "Kerberos Token Authentication"):
        if len(argv) != 3:
            stderr_print("%s invalid arguments" % argv[0])
            stderr_print("usage: %s username token" % argv[0])
            return 1
        username = argv[1]
        token = argv[2]
        kwargs = {"username": username}
        a = Authenticator(**kwargs)
        server_salt, digest = a.get_challenge(("xor", ))
        salt_digest = a.choose_salt_digest(get_digests())
        assert digest == "xor"
        client_salt = get_salt(len(server_salt))
        combined_salt = gendigest(salt_digest, client_salt, server_salt)
        response = xor(token, combined_salt)
        caps = typedict({
            "challenge_response": response,
            "challenge_client_salt": client_salt,
        })
        a.authenticate(caps)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
