# This file is part of Xpra.
# Copyright (C) 2021 Antoine Martin <antoine@xpra.org>
# Xpra is released under the terms of the GNU GPL v2, or, at your option, any
# later version. See the file COPYING for details.

import struct
from threading import RLock
from collections.abc import Callable

from xpra.os_util import gi_import
from xpra.net.rfb.protocol import RFBProtocol
from xpra.net.rfb.const import RFBEncoding, RFBClientMessage, RFBAuth, CLIENT_INIT, AUTH_STR, RFB_KEYS
from xpra.util.str_fn import csv, repr_ellipsized, hexstr
from xpra.log import Logger

GLib = gi_import("GLib")

log = Logger("network", "protocol", "rfb")

WID = 1


def check_wid(wid) -> bool:
    if wid != WID:
        log("ignoring pointer movement outside the VNC window")
        return False
    return True


class RFBClientProtocol(RFBProtocol):

    def __init__(self, conn, process_packet_cb, next_packet):
        self.next_packet = next_packet
        self.rectangles = 0
        self.position = 0, 0
        # translate xpra packets into rfb packets:
        self._rfb_converters: dict[str, Callable] = {
            "pointer-position": self.send_pointer_position,
            "button-action": self.send_button_action,
            "key-action": self.send_key_action,
            "configure-window": self.track_window,
        }
        self.send_lock = RLock()
        super().__init__(conn, process_packet_cb)

    def source_has_more(self) -> None:
        log("source_has_more()")
        if not self.send_lock.acquire(False):
            return
        try:
            while True:
                pdata = self.next_packet()
                packet = pdata[0]
                start_send_cb = pdata[1]
                end_send_cb = pdata[2]
                has_more = pdata[5]
                if start_send_cb:
                    start_send_cb()
                log("packet: %s", packet[0])
                handler = self._rfb_converters.get(packet[0])
                if handler:
                    handler(packet)
                if end_send_cb:
                    end_send_cb()
                if not has_more:
                    break
        finally:
            self.send_lock.release()

    def send_pointer_position(self, packet) -> None:
        log("send_pointer_position(%s)", packet)
        # ['pointer-position', 1, (3348, 582), ['mod2'], []]
        if not check_wid(packet[1]):
            return
        x, y = packet[2]
        # modifiers = packet[3]
        buttons = packet[4]
        button_mask = 0
        for i in range(8):
            if i + 1 in buttons:
                button_mask |= 2 ** i
        self.do_send_pointer_event(button_mask, x, y)

    def send_button_action(self, packet) -> None:
        log("send_button_action(%s)", packet)
        if not check_wid(packet[1]):
            return
        # ["button-action", wid, button, pressed, (x, y), modifiers, buttons]
        # ['button-action', 1, 1, False, (2768, 257), ['mod2'], [1]]
        button = packet[2]
        pressed = packet[3]
        x, y = packet[4]
        button_mask = 0
        if pressed:
            button_mask |= 2 ** button
        if len(packet) >= 7:
            buttons = packet[6]
            for i in range(8):
                if i + 1 in buttons:
                    button_mask |= 2 ** i
        self.do_send_pointer_event(button_mask, x, y)

    def do_send_pointer_event(self, button_mask, x, y) -> None:
        # adjust for window position:
        wx, wy = self.position
        self.send_struct(b"!BBHH", RFBClientMessage.PointerEvent, button_mask, x - wx, y - wy)

    def send_key_action(self, packet) -> None:
        log("send_key_action(%s)", packet)
        if not check_wid(packet[1]):
            return
        # ["key-action", "wid", "keyname", "pressed", "modifiers", "keyval", "string", "keycode", "group"]
        keyname = packet[2]
        if len(keyname) == 1:
            keysym = ord(keyname[0])
        else:
            keysym = RFB_KEYS.get(keyname.lower())
        if not keysym:
            log("no keysym found for %s", packet[2:])
            return
        pressed = packet[3]
        self.send_struct(b"!BBHI", RFBClientMessage.KeyEvent, pressed, 0, keysym)

    def track_window(self, packet) -> None:
        log("track_window(%s)", packet)
        if not check_wid(packet[1]):
            return
        self.position = packet[2], packet[3]
        log("window offset: %s", self.position)
        # ["configure-window", self.wid, sx, sy, sw, sh, props, self._resize_counter, state, skip_geometry]
        # ['configure-window', 1, 0, 37, 1280, 1024,
        #    {'encodings.rgb_formats': ['BGRA', 'BGRX', 'RGBA', 'RGBX', 'BGR', 'RGB', 'r210', 'BGR565'],
        #     'encoding.transparency': False,
        #     'encoding.full_csc_modes': {
        #         'h264': ['ARGB', 'BGRA', 'BGRX', 'GBRP', 'GBRP10', 'GBRP9LE',
        #                  'RGB', 'XRGB', 'YUV420P', 'YUV422P', 'YUV444P', 'YUV444P10', 'r210'],
        #         'vp8': ['YUV420P'], 'h265': ['BGRX', 'GBRP', 'GBRP10', 'GBRP9LE',
        #                  'RGB', 'XRGB', 'YUV420P', 'YUV422P', 'YUV444P', 'YUV444P10', 'r210'],
        #         'mpeg4': ['YUV420P'],
        #         'mpeg1': ['YUV420P'],
        #         'mpeg2': ['YUV420P'],
        #         'vp9': ['YUV420P', 'YUV444P', 'YUV444P10'],
        #         'webp': ['BGRA', 'BGRX', 'RGBA', 'RGBX']
        #     },
        #     'encoding.send-window-size': True,
        #     'encoding.render-size': (1280, 1024),
        #     'encoding.scrolling': True},
        #     0, {}, False, 1, (4582, 1055), ['mod2']))

    def handshake_complete(self) -> None:
        log.info("RFB connected to %s", self._conn.target)
        self._packet_parser = self._parse_security_handshake
        self.send_protocol_handshake()

    def _parse_security_handshake(self, packet) -> int:
        log("parse_security_handshake(%s)", hexstr(packet))
        n = struct.unpack(b"B", packet[:1])[0]
        if n == 0:
            self._internal_error("cannot parse security handshake " + hexstr(packet))
            return 0
        security_types = struct.unpack(b"B" * n, packet[1:])
        st = []
        for v in security_types:
            try:
                v = RFBAuth(v)
            except ValueError:
                pass
            st.append(v)
        log("parse_security_handshake(%s) security_types=%s", hexstr(packet), [AUTH_STR.get(v, v) for v in st])
        if not st or RFBAuth.NONE in st:
            auth_type = RFBAuth.NONE
            # go straight to the result:
            self._packet_parser = self._parse_security_result
        elif RFBAuth.VNC in st:
            auth_type = RFBAuth.VNC
            self._packet_parser = self._parse_vnc_security_challenge
        else:
            self._internal_error("no supported security types in %r" % csv(AUTH_STR.get(v, v) for v in st))
            return 0
        self.send_struct(b"B", auth_type)
        return 1 + n

    def _parse_vnc_security_challenge(self, packet) -> int:
        if len(packet) < 16:
            return 0
        challenge = packet[:16]
        log("parse_vnc_security_challenge(%s)", packet)
        auth_caps = {}
        # this will end up calling send_challenge_reply() with the response,
        # the password will be obtained from the client's challenge handlers,
        # which may prompt the user.
        # (see client base for details)
        self._process_packet_cb(self, ["challenge", challenge, auth_caps, "des", "none"])
        return 16

    def send_challenge_reply(self, challenge_response) -> None:
        log("send_challenge_reply(%s)", challenge_response)
        self._packet_parser = self._parse_security_result
        import binascii  # pylint: disable=import-outside-toplevel
        self.send(binascii.unhexlify(challenge_response))

    def _parse_security_result(self, packet) -> int:
        if len(packet) < 4:
            return 0
        r = struct.unpack(b"I", packet[:4])[0]
        if r != 0:
            self._internal_error(f"authentication denied, server returned {r}")
            return 0
        log("parse_security_result(%s) success", hexstr(packet))
        self._packet_parser = self._parse_client_init
        share = False
        self.send_struct(b"B", bool(share))
        return 4

    def _parse_client_init(self, packet) -> int:
        log("_parse_client_init(%s)", packet)
        ci_size = struct.calcsize(CLIENT_INIT)
        if len(packet) < ci_size:
            return 0
        # the last item in client init is the length of the session name:
        client_init = struct.unpack(CLIENT_INIT, packet[:ci_size])
        name_size = client_init[-1]
        # do we have enough to parse that too?
        if len(packet) < ci_size + name_size:
            return 0
        # w, h, bpp, depth, bigendian, truecolor, rmax, gmax, bmax, rshift, bshift, gshift = client_init[:12]
        w, h, bpp, depth, bigendian, truecolor = client_init[:6]
        sn = packet[ci_size:ci_size + name_size]
        try:
            session_name = sn.decode("utf8")
        except UnicodeDecodeError:
            session_name = sn.decode("latin1")
        log.info(f"RFB server session {session_name!r}: {w}x{h} {depth} bits")
        log(f"bpp={bpp}, bigendian={bool(bigendian)}")
        if not truecolor:
            self.invalid("server is not true color", packet)
            return 0
        # simulate hello:
        self._process_packet_cb(self, ["hello", {
            "session-name": session_name,
            "desktop_size": (w, h),
            "protocol": "rfb",
        }])
        # simulate an xpra window packet:
        metadata = {
            "title": session_name,
            "size-constraints": {
                "maximum-size": (w, h),
                "minimum-size": (w, h),
            },
            # "set-initial-position" : False,
            "window-type": ("NORMAL",),
            "has-alpha": False,
            # "decorations" : True,
            "content-type": "desktop",
        }
        client_properties = {}
        self._process_packet_cb(self, ["new-window", WID, 0, 0, w, h, metadata, client_properties])
        self._packet_parser = self._parse_rfb_packet
        self.send_set_encodings()

        # self.send_refresh_request(0, 0, 0, w, h)

        def request_refresh() -> bool:
            self.send_refresh_request(0, 0, 0, w, h)
            return True

        GLib.timeout_add(1000, request_refresh)
        return ci_size + name_size

    def send_set_encodings(self) -> None:
        self.send_struct("!BBHi", RFBClientMessage.SetEncodings, 0, 1, RFBEncoding.RAW)

    def send_refresh_request(self, incremental, x, y, w, h) -> None:
        self.send_struct("!BBHHHH", RFBClientMessage.FramebufferUpdateRequest, incremental, x, y, w, h)

    def _parse_rfb_packet(self, packet) -> int:
        log("parse_rfb_packet(%s)", repr_ellipsized(packet))
        if len(packet) <= 4:
            return 0
        if packet[:2] != struct.pack(b"!BB", 0, 0):
            self.invalid("unknown packet", packet)
            return 0
        self.rectangles = struct.unpack(b"!H", packet[2:4])[0]
        log("%i rectangles coming up", self.rectangles)
        if self.rectangles > 0:
            self._packet_parser = self._parse_rectangle
        return 4

    def _parse_rectangle(self, packet) -> int:
        header_size = struct.calcsize(b"!HHHHi")
        if len(packet) <= header_size:
            return 0
        x, y, w, h, encoding = struct.unpack(b"!HHHHi", packet[:header_size])
        if encoding != RFBEncoding.RAW:
            self.invalid(f"invalid encoding: {encoding}", packet)
            return 0
        if len(packet) < header_size + w * h * 4:
            return 0
        log("screen update: %s", (x, y, w, h))
        pixels = packet[header_size:header_size + w * h * 4]
        draw = ["draw", WID, x, y, w, h, "rgb32", pixels, 0, w * 4, {}]
        self._process_packet_cb(self, draw)
        self.rectangles -= 1
        if self.rectangles == 0:
            self._packet_parser = self._parse_rfb_packet
        return header_size + w * h * 4

    def send_struct(self, fmt, *args) -> None:
        packet = struct.pack(fmt, *args)
        self.send(packet)
