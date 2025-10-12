# This file is part of Xpra.
# Copyright (C) 2020 Antoine Martin <antoine@xpra.org>
# Xpra is released under the terms of the GNU GPL v2, or, at your option, any
# later version. See the file COPYING for details.

from xpra.os_util import gi_import
from xpra.client.gtk3.menu_helper import MenuHelper
from xpra.platform.gui import get_icon_size
from xpra.log import Logger

log = Logger("gtk", "window")

Gtk = gi_import("Gtk")
Gdk = gi_import("Gdk")


def ticked_icon(state: bool) -> str:
    return "ticked.png" if state else "unticked.png"


class WindowMenuHelper(MenuHelper):

    def __init__(self, client, window):
        super().__init__(client)
        self.window = window

    def get_menu_items(self) -> list[Gtk.ImageMenuItem | Gtk.MenuItem]:
        return [
            # menu.append(self.make_aboutmenuitem())
            self.make_infomenuitem(),
            # if self.client.client_supports_opengl:
            #    menu.append(self.make_openglmenuitem())
            self.make_minimizemenuitem(),
            self.make_maximizemenuitem(),
            self.make_fullscreenmenuitem(),
            self.make_abovenmenuitem(),
            self.make_grabmenuitem(),
            self.make_bordermenuitem(),
            self.make_refreshmenuitem(),
            self.make_reinitmenuitem(),
            self.make_closemenuitem(),
        ]

    def make_infomenuitem(self) -> Gtk.ImageMenuItem:
        def show_info(*_args) -> None:
            from xpra.client.gtk3.window_info import WindowInfo
            wi = WindowInfo(self.client, self.window)
            wi.show()

        gl = self.menuitem("Window Information", "information.png", "Window state and details", show_info)
        gl.set_tooltip_text()
        return gl

    def make_openglmenuitem(self) -> Gtk.ImageMenuItem:
        gl = self.checkitem("OpenGL")
        gl.set_tooltip_text("hardware accelerated rendering using OpenGL")
        return gl

    def make_minimizemenuitem(self) -> Gtk.ImageMenuItem:
        def minimize(*args) -> None:
            log("minimize%s", args)
            self.window.iconify()

        return self.menuitem("Minimize", "minimize.png", cb=minimize)

    def make_maximizemenuitem(self) -> Gtk.ImageMenuItem:
        def maximize(*args) -> None:
            log("maximize%s", args)
            if self.window.is_maximized():
                self.window.unmaximize()
            else:
                self.window.maximize()

        def get_label(maximized) -> str:
            return "Unmaximize" if maximized else "Maximize"

        label = get_label(self.window.is_maximized())
        self.maximize_menuitem = self.menuitem(label, "maximize.png", cb=maximize)

        def window_state_updated(widget, event) -> None:
            maximized_changed = event.changed_mask & Gdk.WindowState.MAXIMIZED
            log("state_changed%s maximized_changed=%s", (widget, event), maximized_changed)
            if maximized_changed:
                lbl = get_label(event.new_window_state & Gdk.WindowState.MAXIMIZED)
                self.maximize_menuitem.set_label(lbl)
            self.maximize_menuitem.set_sensitive(self.window.can_maximize())

        self.window.connect("window-state-event", window_state_updated)
        return self.maximize_menuitem

    def make_fullscreenmenuitem(self) -> Gtk.ImageMenuItem:
        def fullscreen(*args) -> None:
            log("fullscreen%s", args)
            self.window.fullscreen()

        return self.menuitem("Fullscreen", "scaling.png", cb=fullscreen)

    def _set_ticked(self, item, state: bool) -> None:
        icon_name = ticked_icon(state)
        icon_size = self.menu_icon_size or get_icon_size()
        image = self.get_image(icon_name, icon_size)
        item.set_image(image)

    def make_abovenmenuitem(self) -> Gtk.ImageMenuItem:
        def toggle_above(*args) -> None:
            above = not self.window._above
            log("toggle_above%s above=%s", args, above)
            self.window._above = above
            self.window.set_keep_above(above)
            self._set_ticked(self.above_menuitem, above)

        self.above_menuitem = self.menuitem("Always on top", ticked_icon(self.window._above), cb=toggle_above)
        return self.above_menuitem

    def make_grabmenuitem(self) -> Gtk.ImageMenuItem:
        def is_grabbed() -> bool:
            return self.client._window_with_grab == self.window.wid

        def toggle_grab(*args) -> None:
            log("toggle_grab%s", args)
            if is_grabbed():
                self.client.window_ungrab()
            else:
                self.client.window_grab(self.window.wid, self.window)
            self._set_ticked(self.grab_menuitem, is_grabbed())

        self.grab_menuitem = self.menuitem("Grabbed", ticked_icon(is_grabbed()), cb=toggle_grab)
        return self.grab_menuitem

    def make_bordermenuitem(self) -> Gtk.ImageMenuItem:
        def toggle_border(*args) -> None:
            log("toggle_border%s", args)
            self.window.border.shown = not self.window.border.shown
            self._set_ticked(self.grab_menuitem, self.window.border.shown)
            self.client.send_refresh(self.window.wid)

        self.border_menuitem = self.menuitem("Show Border", ticked_icon(self.window.border.shown), cb=toggle_border)
        return self.border_menuitem

    def make_refreshmenuitem(self) -> Gtk.ImageMenuItem:
        def force_refresh(*args) -> None:
            log("force refresh%s", args)
            self.client.send_refresh(self.window.wid)
            reset_icon = getattr(self.window, "reset_icon", None)
            if reset_icon:
                reset_icon()

        return self.menuitem("Refresh", "retry.png", cb=force_refresh)

    def make_reinitmenuitem(self) -> Gtk.ImageMenuItem:
        def force_reinit(*args) -> None:
            log("force reinit%s", args)
            self.client.reinit_window(self.window.wid, self.window)
            reset_icon = getattr(self.window, "reset_icon", None)
            if reset_icon:
                reset_icon()

        return self.menuitem("Re-initialize", "reinitialize.png", cb=force_reinit)

    def make_closemenuitem(self) -> Gtk.ImageMenuItem:
        def close(*args) -> None:
            log("close(%s)", args)
            self.window.close()

        return self.menuitem("Close", "close.png", cb=close)
