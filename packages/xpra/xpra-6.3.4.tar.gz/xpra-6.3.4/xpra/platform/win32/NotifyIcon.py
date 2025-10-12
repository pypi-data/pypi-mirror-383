#!/usr/bin/env python3
# This file is part of Xpra.
# Copyright (C) 2011 Antoine Martin <antoine@xpra.org>
# Xpra is released under the terms of the GNU GPL v2, or, at your option, any
# later version. See the file COPYING for details.

# Low level support for the "system tray" on MS Windows
# Based on code from winswitch, itself based on "win32gui_taskbar demo"

import os
from ctypes import (
    Structure, byref, addressof, c_void_p, sizeof, POINTER,
    get_last_error, WinError, WinDLL, HRESULT,  # @UnresolvedImport
)
from ctypes.wintypes import HWND, UINT, POINT, HICON, BOOL, CHAR, WCHAR, DWORD, HMODULE, RECT
from typing import Any
from collections.abc import Callable, Sequence

from xpra.util.objects import typedict
from xpra.util.str_fn import csv, bytestostr
from xpra.util.env import envbool
from xpra.common import noop, XPRA_GUID1, XPRA_GUID2, XPRA_GUID3, XPRA_GUID4
from xpra.platform.win32 import constants as win32con
from xpra.platform.win32.icon_util import image_to_ICONINFO
from xpra.platform.win32.common import (
    GUID, WNDCLASSEX, WNDPROC,
    GetSystemMetrics,
    EnumDisplayMonitors,
    GetCursorPos,
    PostMessageA,
    CreateWindowExA, CreatePopupMenu, AppendMenu,
    LoadIconA,
    DefWindowProcA, RegisterWindowMessageA, RegisterClassExA,
    LoadImageW, DestroyIcon,
    UpdateWindow, DestroyWindow,
    PostQuitMessage,
    GetModuleHandleExA,
    GetStockObject,
)
from xpra.log import Logger

log = Logger("tray", "win32")
geomlog = Logger("tray", "geometry")

log("loading ctypes NotifyIcon functions")

TRAY_ALPHA = envbool("XPRA_TRAY_ALPHA", True)


def GetProductInfo(dwOSMajorVersion=5, dwOSMinorVersion=0, dwSpMajorVersion=0, dwSpMinorVersion=0):
    product_type = DWORD(0)
    from xpra.platform.win32.common import GetProductInfo as k32GetProductInfo
    v = k32GetProductInfo(dwOSMajorVersion, dwOSMinorVersion, dwSpMajorVersion, dwSpMinorVersion, byref(product_type))
    log("GetProductInfo(%i, %i, %i, %i)=%i product_type=%s",
        dwOSMajorVersion, dwOSMinorVersion, dwSpMajorVersion, dwSpMinorVersion, v, hex(product_type.value))
    return bool(v)


# MAX_TIP_SIZE = 128
MAX_TIP_SIZE = 64


# noinspection PyTypeChecker
def getNOTIFYICONDATAClass(char_type=CHAR, tip_size: int = MAX_TIP_SIZE):
    class _NOTIFYICONDATA(Structure):
        _fields_ = (
            ("cbSize", DWORD),
            ("hWnd", HWND),
            ("uID", UINT),
            ("uFlags", UINT),
            ("uCallbackMessage", UINT),
            ("hIcon", HICON),
            ("szTip", char_type * tip_size),
            ("dwState", DWORD),
            ("dwStateMask", DWORD),
            ("szInfo", char_type * 256),
            ("uVersion", UINT),
            ("szInfoTitle", char_type * 64),
            ("dwInfoFlags", DWORD),
            ("guidItem", GUID),
            ("hBalloonIcon", HICON),
        )

    return _NOTIFYICONDATA


NOTIFYICONDATAA = getNOTIFYICONDATAClass()
NOTIFYICONDATAW = getNOTIFYICONDATAClass(WCHAR)

shell32 = WinDLL("shell32", use_last_error=True)
Shell_NotifyIconA = shell32.Shell_NotifyIconA
Shell_NotifyIconA.restype = BOOL
Shell_NotifyIconA.argtypes = [DWORD, c_void_p]
Shell_NotifyIconW = shell32.Shell_NotifyIconW
Shell_NotifyIconW.restype = BOOL
Shell_NotifyIconW.argtypes = [DWORD, c_void_p]
Shell_NotifyIconGetRect = shell32.Shell_NotifyIconGetRect
SHSTDAPI = HRESULT


class NOTIFYICONIDENTIFIER(Structure):
    _fields_ = (
        ("cbSize", DWORD),
        ("hWnd", HWND),
        ("uID", UINT),
        ("guidItem", GUID),
    )


PNOTIFYICONIDENTIFIER = POINTER(NOTIFYICONIDENTIFIER)
Shell_NotifyIconGetRect.restype = SHSTDAPI
Shell_NotifyIconGetRect.argtypes = [PNOTIFYICONIDENTIFIER, POINTER(RECT)]

Shell_NotifyIcon = Shell_NotifyIconA
NOTIFYICONDATA = NOTIFYICONDATAA

XPRA_GUID = GUID()
XPRA_GUID.Data1 = XPRA_GUID1
XPRA_GUID.Data2 = XPRA_GUID2
XPRA_GUID.Data3 = XPRA_GUID3
XPRA_GUID.Data4 = XPRA_GUID4

FALLBACK_ICON = LoadIconA(0, win32con.IDI_APPLICATION)

# constants found in win32gui:
NIM_ADD = 0
NIM_MODIFY = 1
NIM_DELETE = 2
NIM_SETFOCUS = 3
NIM_SETVERSION = 4

NIF_MESSAGE = 1
NIF_ICON = 2
NIF_TIP = 4
NIF_STATE = 8
NIF_INFO = 16
NIF_GUID = 32
NIF_REALTIME = 64
NIF_SHOWTIP = 128

NIF_FLAGS = {
    NIF_MESSAGE: "MESSAGE",
    NIF_ICON: "ICON",
    NIF_TIP: "TIP",
    NIF_STATE: "STATE",
    NIF_INFO: "INFO",
    NIF_GUID: "GUID",
    NIF_REALTIME: "REALTIME",
    NIF_SHOWTIP: "SHOWTIP",
}

# found here:
# http://msdn.microsoft.com/en-us/library/windows/desktop/ff468877(v=vs.85).aspx
WM_XBUTTONDOWN = 0x020B
WM_XBUTTONUP = 0x020C
WM_XBUTTONDBLCLK = 0x020D

BUTTON_MAP: dict[int, list[tuple[int, int]]] = {
    win32con.WM_LBUTTONDOWN: [(1, 1)],
    win32con.WM_LBUTTONUP: [(1, 0)],
    win32con.WM_MBUTTONDOWN: [(2, 1)],
    win32con.WM_MBUTTONUP: [(2, 0)],
    win32con.WM_RBUTTONDOWN: [(3, 1)],
    win32con.WM_RBUTTONUP: [(3, 0)],
    win32con.WM_LBUTTONDBLCLK: [(1, 1), (1, 0)],
    win32con.WM_MBUTTONDBLCLK: [(2, 1), (2, 0)],
    win32con.WM_RBUTTONDBLCLK: [(3, 1), (3, 0)],
    WM_XBUTTONDOWN: [(4, 1)],
    WM_XBUTTONUP: [(4, 0)],
    WM_XBUTTONDBLCLK: [(4, 1), (4, 0)],
}


class win32NotifyIcon:
    # we register the windows event handler on the class,
    # this allows us to know which hwnd refers to which instance:
    instances: dict[int, Any] = {}

    def __init__(self, app_id: int = 0, title: str = "",
                 move_callback: Callable = noop,
                 click_callback: Callable = noop,
                 exit_callback: Callable = noop,
                 command_callback: Callable = noop,
                 iconPathName: str = ""):
        log("win32NotifyIcon: app_id=%i, title=%r", app_id, title)
        self.app_id = app_id
        self.title = title
        self.current_icon = None
        self.destroy_icon = None
        self.move_callback = move_callback
        self.click_callback = click_callback
        self.exit_callback = exit_callback
        self.command_callback = command_callback
        self.reset_function: tuple[Callable, Sequence[Any]] | None = None
        self.image_cache: dict[str, Any] = {}
        # Create the Window.
        if iconPathName:
            self.current_icon = self.LoadImage(iconPathName) or FALLBACK_ICON
        self.create_tray_window()

    def __repr__(self):
        return "win32NotifyIcon(%#x)" % self.app_id

    def create_tray_window(self) -> None:
        log("create_tray_window()")
        self.create_window()
        self.register_tray()

    def create_window(self) -> None:
        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        window_name = "%s StatusIcon Window" % bytestostr(self.title)
        niwc = get_notifyicon_wnd_class()
        args = (0, niwc.NIclassAtom, window_name, style,
                win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT, 0, 0,
                0, 0, niwc.hInstance, 0)
        log("CreateWindowExA%s", args)
        self.hwnd = CreateWindowExA(*args)
        log("create_window() hwnd=%#x", self.hwnd or 0)
        if not self.hwnd:
            raise WinError(get_last_error())
        TASKBAR_CREATED = RegisterWindowMessageA(b"TaskbarCreated")
        log(f"{TASKBAR_CREATED=}")
        message_map[TASKBAR_CREATED] = win32NotifyIcon.OnTrayRestart
        UpdateWindow(self.hwnd)
        # register callbacks:
        win32NotifyIcon.instances[self.hwnd] = self

    def register_tray(self) -> None:
        ni = self.make_nid(NIF_ICON | NIF_MESSAGE | NIF_TIP)
        r = Shell_NotifyIcon(NIM_ADD, byref(ni))
        log("Shell_NotifyIcon ADD=%i", r)
        if not r:
            raise RuntimeError("Shell_NotifyIcon failed to ADD, is explorer.exe running?")

    def make_nid(self, flags) -> NOTIFYICONDATA:
        assert self.hwnd
        nid = NOTIFYICONDATA()
        nid.cbSize = sizeof(NOTIFYICONDATA)
        nid.hWnd = self.hwnd
        nid.uCallbackMessage = win32con.WM_MENUCOMMAND
        nid.hIcon = self.current_icon
        # don't ask why we have to use sprintf to get what we want:
        title = bytestostr(self.title[:MAX_TIP_SIZE - 1])
        try:
            nid.szTip = title
        except (TypeError, ValueError):
            nid.szTip = title.encode()
        nid.dwState = 0
        nid.dwStateMask = 0
        nid.guidItem = XPRA_GUID
        nid.uID = self.app_id
        flags |= NIF_GUID
        # balloon notification bits:
        # szInfo
        # uTimeout
        # szInfoTitle
        # dwInfoFlags
        # hBalloonIcon
        # flags |= NIF_SHOWTIP
        nid.uVersion = 4
        nid.uFlags = flags
        log("make_nid(..)=%s tooltip=%r, app_id=%i, actual flags=%s",
            nid, title, self.app_id, csv([v for k, v in NIF_FLAGS.items() if k & flags]))
        return nid

    def delete_tray_window(self) -> None:
        if not self.hwnd:
            return
        try:
            nid = NOTIFYICONDATA()
            nid.cbSize = sizeof(NOTIFYICONDATA)
            nid.hWnd = self.hwnd
            nid.uID = self.app_id
            nid.guidItem = XPRA_GUID
            nid.uFlags = NIF_GUID
            log("delete_tray_window(..) calling Shell_NotifyIcon(NIM_DELETE, %s)", nid)
            r = Shell_NotifyIcon(NIM_DELETE, byref(nid))
            log("Shell_NotifyIcon(NIM_DELETE, nid)=%s", bool(r))
            ci = self.current_icon
            di = self.destroy_icon
            if ci and di:
                self.current_icon = None
                self.destroy_icon = None
                di(ci)
        except Exception as e:
            log("delete_tray_window()", exc_info=True)
            log.error("Error: failed to delete tray window")
            log.estr(e)

    def get_geometry(self):
        # we can only use this if there is a single monitor
        # because multi-monitor coordinates may have offsets
        # we don't know about (done inside GTK)
        n = len(EnumDisplayMonitors())
        if n == 1:
            nii = NOTIFYICONIDENTIFIER()
            nii.cbSize = sizeof(NOTIFYICONIDENTIFIER)
            nii.hWnd = self.hwnd
            nii.uID = self.app_id
            # nii.guidItem = XPRA_GUID
            rect = RECT()
            if Shell_NotifyIconGetRect(byref(nii), byref(rect)) == 0:  # NOSONAR
                geom = (rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top)
                geomlog("Shell_NotifyIconGetRect: %s", geom)
                return geom
        return None

    def set_blinking(self, on) -> None:
        # implement blinking on win32 using a timer?
        pass

    def set_tooltip(self, tooltip: str) -> None:
        log("set_tooltip(%r)", tooltip)
        self.title = tooltip
        nid = self.make_nid(NIF_ICON | NIF_MESSAGE | NIF_TIP)
        Shell_NotifyIcon(NIM_MODIFY, byref(nid))

    def set_icon(self, iconPathName: str) -> None:
        log("set_icon(%s)", iconPathName)
        hicon = self.LoadImage(iconPathName) or FALLBACK_ICON
        self.do_set_icon(hicon)
        nid = self.make_nid(NIF_ICON)
        Shell_NotifyIcon(NIM_MODIFY, byref(nid))
        self.reset_function = self.set_icon, (iconPathName,)

    def do_set_icon(self, hicon, destroy_icon=None) -> None:
        log("do_set_icon(%#x)", hicon)
        ci = self.current_icon
        di = self.destroy_icon
        if ci and ci != hicon and di:
            di(ci)
        self.current_icon = hicon
        self.destroy_icon = destroy_icon
        nid = self.make_nid(NIF_ICON)
        Shell_NotifyIcon(NIM_MODIFY, byref(nid))

    def set_icon_from_data(self, pixels, has_alpha: bool, w: int, h: int, rowstride: int, options=None) -> None:
        # this is convoluted but it works..
        log("set_icon_from_data%s", ("%s pixels" % len(pixels), has_alpha, w, h, rowstride, options))
        from PIL import Image
        if has_alpha:
            img_format = "RGBA"
        else:
            img_format = "RGBX"
        rgb_format = typedict(options or {}).strget("rgb_format", "RGBA")
        img = Image.frombuffer(img_format, (w, h), pixels, "raw", rgb_format, rowstride, 1)
        assert img, "failed to load image from buffer (%i bytes for %ix%i %s)" % (len(pixels), w, h, rgb_format)
        # apparently, we have to use SM_CXSMICON (small icon) and not SM_CXICON (regular size):
        icon_w = GetSystemMetrics(win32con.SM_CXSMICON)
        icon_h = GetSystemMetrics(win32con.SM_CYSMICON)
        if w != icon_w or h != icon_h:
            log("resizing tray icon to %ix%i", icon_w, icon_h)
            try:
                LANCZOS = Image.Resampling.LANCZOS
            except AttributeError:
                LANCZOS = Image.LANCZOS
            img = img.resize((icon_w, icon_h), LANCZOS)
            rowstride = w * 4
        hicon = image_to_ICONINFO(img, TRAY_ALPHA) or FALLBACK_ICON
        self.do_set_icon(hicon, DestroyIcon)
        UpdateWindow(self.hwnd)
        self.reset_function = self.set_icon_from_data, (pixels, has_alpha, w, h, rowstride, options)

    def LoadImage(self, iconPathName: str):
        if not iconPathName:
            return None
        image = self.image_cache.get(iconPathName)
        if not image:
            image = self.doLoadImage(iconPathName)
            self.image_cache[iconPathName] = image
        return image

    def doLoadImage(self, iconPathName: str):
        mingw_prefix = os.environ.get("MINGW_PREFIX")
        if mingw_prefix and iconPathName.find(mingw_prefix) >= 0:
            # python can deal with mixed win32 and unix paths,
            # but the native win32 LoadImage function cannot,
            # this happens when running from a mingw environment
            iconPathName = iconPathName.replace("/", "\\")
        icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
        try:
            assert os.path.exists(iconPathName), "icon '%s' not found" % iconPathName
            img_type = win32con.IMAGE_ICON
            if iconPathName.lower().split(".")[-1] in ("png", "bmp"):
                img_type = win32con.IMAGE_BITMAP
                icon_flags |= win32con.LR_CREATEDIBSECTION | win32con.LR_LOADTRANSPARENT
            log("LoadImage(%s) using image type=%s", iconPathName,
                {
                    win32con.IMAGE_ICON: "ICON",
                    win32con.IMAGE_BITMAP: "BITMAP",
                }.get(img_type))
            niwc = get_notifyicon_wnd_class()
            v = LoadImageW(niwc.hInstance, iconPathName, img_type, 0, 0, icon_flags)
            assert v is not None
        except Exception:
            log.error("Error: failed to load icon '%s'", iconPathName, exc_info=True)
            return None
        else:
            log("LoadImage(%s)=%#x", iconPathName, v)
            return v

    def OnTrayRestart(self, hwnd=0, msg=0, wparam=0, lparam=0) -> None:
        rfn = self.reset_function
        try:
            # re-create the tray window:
            self.delete_tray_window()
            self.register_tray()
            # now try to repaint the tray:
            log("OnTrayRestart%s reset function: %s", (hwnd, msg, wparam, lparam), rfn)
            if rfn:
                rfn[0](*rfn[1])
        except Exception as e:
            log.error("Error: cannot reset tray icon")
            log.error(f" using {rfn}")
            log.estr(e)

    def OnCommand(self, hwnd: int, msg: int, wparam: int, lparam: int):
        cb = self.command_callback
        log("OnCommand%s callback=%s", (hwnd, msg, wparam, lparam), cb)
        if cb:
            cid = wparam & 0xFFFF
            cb(hwnd, cid)

    def OnDestroy(self, hwnd: int, msg: int, wparam: int, lparam: int) -> None:
        log("OnDestroy%s", (hwnd, msg, wparam, lparam))
        self.destroy()

    def OnTaskbarNotify(self, hwnd: int, msg: int, wparam: int, lparam: int) -> int:
        if lparam == win32con.WM_MOUSEMOVE:
            cb = self.move_callback
            bm = [(hwnd, int(msg), int(wparam), int(lparam))]
        else:
            cb = self.click_callback
            bm = BUTTON_MAP.get(lparam, [])
        log("OnTaskbarNotify%s button(s) lookup: %s, callback=%s", (hwnd, msg, wparam, lparam), bm, cb)
        for button_event in bm:
            cb(*button_event)
        return 1

    def close(self) -> None:
        log("win32NotifyIcon.close()")
        self.destroy()

    def destroy(self) -> None:
        cb = self.exit_callback
        hwnd = self.hwnd
        log("destroy() hwnd=%#x, exit callback=%s", hwnd, cb)
        self.delete_tray_window()
        self.exit_callback = noop
        with log.trap_error("Error on exit callback %s", cb):
            cb()
        if hwnd:
            win32NotifyIcon.instances.pop(hwnd, None)


WM_TRAY_EVENT = win32con.WM_MENUCOMMAND  # a message id we choose
log(f"{WM_TRAY_EVENT=}")

message_map: dict[int, Callable] = {
    win32con.WM_DESTROY: win32NotifyIcon.OnDestroy,
    win32con.WM_COMMAND: win32NotifyIcon.OnCommand,
    WM_TRAY_EVENT: win32NotifyIcon.OnTaskbarNotify,
}


def NotifyIconWndProc(hwnd, msg, wParam, lParam):
    instance = win32NotifyIcon.instances.get(hwnd)
    fn = message_map.get(msg)

    def i(v):
        try:
            return int(v)
        except (ValueError, TypeError):
            return v

    log("NotifyIconWndProc%s instance=%s, message(%i)=%s", (i(hwnd), i(msg), i(wParam), i(lParam)), instance, msg, fn)
    # log("potential matching win32 constants for message: %s", [x for x in dir(win32con) if getattr(win32con, x)==msg])
    if instance and fn:
        return fn(instance, hwnd, msg, wParam, lParam) or 0
    return DefWindowProcA(hwnd, msg, wParam, lParam)


_notifyicon_wnd_class = None


def get_notifyicon_wnd_class():
    global _notifyicon_wnd_class
    if _notifyicon_wnd_class is None:
        hmodule = HMODULE(0)
        assert GetModuleHandleExA(0, None, byref(hmodule))
        log("GetModuleHandleExA(..)=%#x", int(hmodule.value))

        NIwc = WNDCLASSEX()
        NIwc.cbSize = sizeof(WNDCLASSEX)
        NIwc.style = win32con.CS_HREDRAW | win32con.CS_VREDRAW
        NIwc.lpfnWndProc = WNDPROC(NotifyIconWndProc)
        NIwc.hInstance = hmodule
        NIwc.hBrush = GetStockObject(win32con.WHITE_BRUSH)
        NIwc.lpszClassName = "win32NotifyIcon"

        NIclassAtom = RegisterClassExA(byref(NIwc))
        log("RegisterClassExA(%s)=%i", NIwc.lpszClassName, NIclassAtom)
        if NIclassAtom == 0:
            raise WinError(get_last_error())
        NIwc.NIclassAtom = NIclassAtom
        _notifyicon_wnd_class = NIwc
    return _notifyicon_wnd_class


def main(args):
    from xpra.platform.win32.common import user32
    from ctypes.wintypes import MSG

    if "-v" in args:
        from xpra.log import enable_debug_for
        enable_debug_for("all")

    log.warn("main")

    def click_callback(_button, _pressed):
        menu = CreatePopupMenu()
        AppendMenu(menu, win32con.MF_STRING, 1024, "Generate balloon")
        AppendMenu(menu, win32con.MF_STRING, 1025, "Exit")
        pos = POINT()
        GetCursorPos(addressof(pos))  # NOSONAR
        hwnd = tray.hwnd
        user32.SetForegroundWindow(hwnd)
        user32.TrackPopupMenu(menu, win32con.TPM_LEFTALIGN, pos.x, pos.y, 0, hwnd, None)  # @UndefinedVariable
        PostMessageA(hwnd, win32con.WM_NULL, 0, 0)

    def command_callback(hwnd, cid):
        if cid == 1024:
            from xpra.platform.win32.balloon import notify
            try:
                from PIL import Image
                from io import BytesIO
                img = Image.open("icons\\printer.png")
                buf = BytesIO()
                img.save(buf, "PNG")
                data = buf.getvalue()
                buf.close()
                icon = (b"png", img.size[0], img.size[1], data)
            except Exception as e:
                print(f"could not find icon: {e}")
                icon = None
            notify(hwnd, 0, "hello", "world", timeout=1000, icon=icon)
        elif cid == 1025:
            print("Goodbye")
            DestroyWindow(hwnd)
        else:
            print("OnCommand for ID=%s" % cid)

    def win32_quit(*_args):
        PostQuitMessage(0)  # Terminate the app.

    from xpra.platform.paths import get_icon_dir, get_app_dir
    for idir in (get_icon_dir(), get_app_dir(), "fs/share/xpra/icons"):
        ipath = os.path.abspath(os.path.join(idir, "xpra.ico"))
        if os.path.exists(ipath):
            break
    tray = win32NotifyIcon(999, "test", move_callback=noop, click_callback=click_callback, exit_callback=win32_quit,
                           command_callback=command_callback, iconPathName=ipath)
    import signal
    signal.signal(signal.SIGINT, win32_quit)
    signal.signal(signal.SIGTERM, win32_quit)

    # pump messages:
    msg = MSG()
    p_msg = addressof(msg)  # NOSONAR
    while user32.GetMessageA(p_msg, win32con.NULL, 0, 0) != 0:
        user32.TranslateMessage(p_msg)
        user32.DispatchMessageA(p_msg)


if __name__ == '__main__':
    import sys

    main(sys.argv)
