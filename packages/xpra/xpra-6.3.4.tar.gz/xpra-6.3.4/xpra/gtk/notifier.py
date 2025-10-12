#!/usr/bin/env python3
#
# gtkPopupNotify.py
#
# Copyright (C) 2009 Daniel Woodhouse
# Copyright (C) 2013 Antoine Martin <antoine@xpra.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from xpra.os_util import OSX, gi_import
from xpra.gtk.window import add_close_accel
from xpra.gtk.widget import label, modify_fg, color_parse
from xpra.gtk.pixbuf import get_icon_pixbuf
from xpra.notifications.notifier_base import NotifierBase, log, NID

Gtk = gi_import("Gtk")
Gdk = gi_import("Gdk")
GLib = gi_import("GLib")
GdkPixbuf = gi_import("GdkPixbuf")

DEFAULT_FG_COLOUR = None
DEFAULT_BG_COLOUR = None
if OSX:
    # black on white fits better with osx
    DEFAULT_FG_COLOUR = color_parse("black")
    DEFAULT_BG_COLOUR = color_parse("#f2f2f2")
DEFAULT_WIDTH = 340
DEFAULT_HEIGHT = 100


class GTKNotifier(NotifierBase):

    def __init__(self, closed_cb=None, action_cb=None, size_x=DEFAULT_WIDTH, size_y=DEFAULT_HEIGHT, timeout=5):
        super().__init__(closed_cb, action_cb)
        self.handles_actions = True
        """
        Create a new notification stack.  The recommended way to create Popup instances.
          Parameters:
            `size_x` : The desired width of the notifications.
            `size_y` : The desired minimum height of the notifications. If the text is
            longer it will be expanded to fit.
            `timeout` : Popup instance will disappear after this timeout if there
            is no human intervention. This can be overridden temporarily by passing
            a new timeout to the new_popup method.
        """
        self.size_x = size_x
        self.size_y = size_y
        self.timeout = timeout
        """
        Other parameters:
        These will take effect for every popup created after the change.
            `max_popups` : The maximum number of popups to be shown on the screen
            at one time.
            `bg_color` : if None default is used (usually grey). set with a gdk.Color.
            `fg_color` : if None default is used (usually black). set with a gdk.Color.
            `show_timeout : if True, a countdown till destruction will be displayed.

        """
        self.max_popups = 5
        self.fg_color = DEFAULT_FG_COLOUR
        self.bg_color = DEFAULT_BG_COLOUR
        self.show_timeout = False

        self._notify_stack = []
        self._offset = 0

        display = Gdk.Display.get_default()
        n = display.get_n_monitors()
        log("monitors=%s", n)
        # if n<2:
        monitor = display.get_monitor(0)
        geom = monitor.get_geometry()
        self.max_width = geom.width
        self.max_height = geom.height
        log("first monitor dimensions: %dx%d", self.max_width, self.max_height)
        self.x = self.max_width - 20  # keep away from the edge
        self.y = self.max_height - 64  # space for a panel
        log("our reduced dimensions: %dx%d", self.x, self.y)

    def cleanup(self):
        popups = tuple(self._notify_stack)
        self._notify_stack = []
        for x in popups:
            x.hide_notification()
        super().cleanup()

    def get_origin_x(self):
        return self.x

    def get_origin_y(self):
        return self.y

    def close_notify(self, nid):
        for x in self._notify_stack:
            if x.nid == nid:
                x.hide_notification()

    def show_notify(self, dbus_id, tray, nid: NID,
                    app_name: str, replaces_nid: NID, app_icon,
                    summary: str, body: str, actions, hints, timeout, icon):
        GLib.idle_add(self.new_popup, int(nid), summary, body, actions, icon, timeout, 0 < timeout <= 600)

    def new_popup(self, nid: int, summary: str, body: str, actions: tuple, icon, timeout=10 * 1000, show_timeout=False):
        """Create a new Popup instance, or update an existing one """
        existing = [p for p in self._notify_stack if p.nid == nid]
        if existing:
            existing[0].set_content(summary, body, actions, icon)
            return
        if len(self._notify_stack) == self.max_popups:
            oldest = self._notify_stack[0]
            oldest.hide_notification()
            self.popup_closed(oldest.nid, 4)
        image = None
        if icon and icon[0] == "png":
            img_data = icon[3]
            loader = GdkPixbuf.PixbufLoader()
            loader.write(img_data)
            loader.close()
            image = loader.get_pixbuf()
        popup = Popup(self, nid, summary, body, actions, image=image, timeout=timeout // 1000,
                      show_timeout=show_timeout)
        self._notify_stack.append(popup)
        self._offset += self._notify_stack[-1].h
        return False

    def destroy_popup_cb(self, popup):
        if popup in self._notify_stack:
            self._notify_stack.remove(popup)
            # move popups down if required
            offset = 0
            for note in self._notify_stack:
                offset = note.reposition(offset, self)
            self._offset = offset

    def popup_closed(self, nid, reason, text=""):
        if self.closed_cb:
            self.closed_cb(nid, reason, text)

    def popup_action(self, nid, action_id):
        if self.action_cb:
            self.action_cb(nid, action_id)


class Popup(Gtk.Window):
    def __init__(self, stack, nid, title, message, actions, image, timeout=5, show_timeout=False):
        log("Popup%s", (stack, nid, title, message, actions, image, timeout, show_timeout))
        self.stack = stack
        self.nid = nid
        super().__init__()

        self.set_accept_focus(False)
        self.set_focus_on_map(False)
        self.set_size_request(stack.size_x, -1)
        self.set_decorated(False)
        self.set_deletable(False)
        self.set_property("skip-pager-hint", True)
        self.set_property("skip-taskbar-hint", True)
        self.connect("enter-notify-event", self.on_hover, True)
        self.connect("leave-notify-event", self.on_hover, False)
        self.set_opacity(0.2)
        self.set_keep_above(True)
        self.destroy_cb = stack.destroy_popup_cb
        self.popup_closed = stack.popup_closed
        self.action_cb = stack.popup_action

        main_box = Gtk.VBox()
        header_box = Gtk.HBox()
        self.header = label()
        self.header.set_padding(3, 3)
        self.header.set_alignment(0, 0)
        header_box.pack_start(self.header, True, True, 5)
        icon = get_icon_pixbuf("close.png")
        if icon:
            close_button = Gtk.Image()
            close_button.set_from_pixbuf(icon)
            close_button.set_padding(3, 3)
            close_window = Gtk.EventBox()
            close_window.set_visible_window(False)
            close_window.connect("button-press-event", self.user_closed)
            close_window.add(close_button)
            close_window.set_size_request(icon.get_width(), icon.get_height())
            header_box.pack_end(close_window, False, False, 0)
        main_box.pack_start(header_box)

        body_box = Gtk.HBox()
        self.image = Gtk.Image()
        self.image.set_size_request(70, 70)
        self.image.set_alignment(0, 0)
        body_box.pack_start(self.image, False, False, 5)
        self.message = label()
        self.message.set_max_width_chars(80)
        self.message.set_size_request(stack.size_x - 90, -1)
        self.message.set_line_wrap(True)
        self.message.set_alignment(0, 0)
        self.message.set_padding(5, 10)
        self.counter = label()
        self.counter.set_alignment(1, 1)
        self.counter.set_padding(3, 3)
        self.timeout = timeout

        body_box.pack_start(self.message, True, False, 5)
        body_box.pack_end(self.counter, False, False, 5)
        main_box.pack_start(body_box, False, False, 5)

        self.buttons_box = Gtk.HBox(homogeneous=True)
        alignment = Gtk.Alignment(xalign=1.0, yalign=0.5, xscale=0.0, yscale=0.0)
        alignment.add(self.buttons_box)
        main_box.pack_start(alignment)
        self.add(main_box)
        if stack.bg_color is not None:
            self.modify_bg(Gtk.StateType.NORMAL, stack.bg_color)
        if stack.fg_color is not None:
            for widget in (self.message, self.header, self.counter):
                modify_fg(widget, stack.fg_color)
        self.show_timeout = show_timeout
        self.hover = False
        self.show_all()
        self.w = self.get_preferred_width()[0]
        self.h = self.get_preferred_height()[0]
        self.move(self.get_x(self.w), self.get_y(self.h))
        self.wait_timer = 0
        self.fade_out_timer = 0
        self.fade_in_timer = GLib.timeout_add(100, self.fade_in)
        # populate the window:
        self.set_content(title, message, actions, image)
        # ensure we don't show it in the taskbar:
        self.realize()
        self.get_window().set_skip_taskbar_hint(True)
        self.get_window().set_skip_pager_hint(True)
        add_close_accel(self, self.user_closed)

    def set_content(self, title, message, actions=(), image=None):
        self.header.set_markup("<b>%s</b>" % title)
        self.message.set_text(message)
        # remove any existing actions:
        for w in tuple(self.buttons_box.get_children()):
            self.buttons_box.remove(w)
        while len(actions) >= 2:
            action_id, action_text = actions[:2]
            actions = actions[2:]
            button = self.action_button(action_id, action_text)
            self.buttons_box.add(button)
        self.buttons_box.show_all()
        if image:
            self.image.show()
            self.image.set_from_pixbuf(image)
        else:
            self.image.hide()

    def action_button(self, action_id, action_text):
        button = Gtk.Button(label=action_text)
        button.set_relief(Gtk.ReliefStyle.NORMAL)

        def popup_cb_clicked(*args):
            self.hide_notification()
            log("popup_cb_clicked%s for action_id=%s, action_text=%s", args, action_id, action_text)
            self.action_cb(self.nid, action_id)

        button.connect("clicked", popup_cb_clicked)
        return button

    def get_x(self, w):
        x = self.stack.get_origin_x() - w // 2
        if (x + w) >= self.stack.max_width:  # don't overflow on the right
            x = self.stack.max_width - w
        x = max(0, x)  # or on the left
        log("get_x(%s)=%s", w, x)
        return x

    def get_y(self, h):
        y = self.stack.get_origin_y()
        if y >= (self.stack.max_height // 2):  # if near bottom, subtract window height
            y = y - h
        if (y + h) >= self.stack.max_height:
            y = self.stack.max_height - h
        y = max(0, y)
        log("get_y(%s)=%s", h, y)
        return y

    def reposition(self, offset, stack):
        """Move the notification window down, when an older notification is removed"""
        log("reposition(%s, %s)", offset, stack)
        new_offset = self.h + offset
        GLib.idle_add(self.move, self.get_x(self.w), self.get_y(new_offset))
        return new_offset

    def fade_in(self):
        opacity = self.get_opacity()
        opacity += 0.15
        if opacity >= 1:
            self.wait_timer = GLib.timeout_add(1000, self.wait)
            self.fade_in_timer = 0
            return False
        self.set_opacity(opacity)
        return True

    def wait(self):
        if not self.hover:
            self.timeout -= 1
        if self.show_timeout:
            self.counter.set_markup(str("<b>%s</b>" % max(0, self.timeout)))
        if self.timeout <= 0:
            self.fade_out_timer = GLib.timeout_add(100, self.fade_out)
            self.wait_timer = 0
            return False
        return True

    def fade_out(self):
        opacity = self.get_opacity()
        opacity -= 0.10
        if opacity <= 0:
            self.in_progress = False
            self.hide_notification()
            self.fade_out_timer = 0  # redundant
            self.popup_closed(self.nid, 1)
            return False
        self.set_opacity(opacity)
        return True

    def on_hover(self, _window, _event, hover):
        """Starts/Stops the notification timer on a mouse in/out event"""
        self.hover = hover

    def user_closed(self, *_args):
        self.hide_notification()
        self.popup_closed(self.nid, 2)

    def hide_notification(self):
        """Destroys the notification and tells the stack to move the
        remaining notification windows"""
        log("hide_notification()")
        for timer in ("fade_in_timer", "fade_out_timer", "wait_timer"):
            v = getattr(self, timer)
            if v:
                setattr(self, timer, None)
                GLib.source_remove(v)
        # destroy window from the UI thread:
        GLib.idle_add(self.destroy)
        self.close()
        self.destroy_cb(self)


def main():
    # example usage
    import random
    color_combos = (("red", "white"), ("white", "blue"), ("green", "black"))
    messages: list[tuple[int, str, str, tuple]] = [
        (1, "Hello", "This is a popup", ()),
        (2, "Actions", "This notification has 3 actions", (1, "Action 1", 2, "Action 2", 3, "Action 3")),
        (3, "Some Latin", "Quidquid latine dictum sit, altum sonatur.", ()),
        (4, "A long message", "The quick brown fox jumped over the lazy dog. " * 6, ()),
        (1, "Hello Again", "Replacing the first notification", ()),
        (2, "Actions Again", "Replacing with just 1 action", (999, "Action 999")),
    ]

    # images = ("logo1_64.png", None)

    def notify_factory():
        color = random.choice(color_combos)
        nid, title, message, actions = messages.pop(0)
        icon = ()  # random.choice(images)
        notifier.bg_color = color_parse(color[0])
        notifier.fg_color = color_parse(color[1])
        notifier.show_timeout = random.choice((True, False))
        notifier.new_popup(nid, title, message, actions, icon)
        return len(messages)

    def gtk_main_quit():
        print("quitting")
        Gtk.main_quit()

    notifier = GTKNotifier(timeout=6)
    GLib.timeout_add(4000, notify_factory)
    GLib.timeout_add(30000, gtk_main_quit)
    Gtk.main()


if __name__ == "__main__":
    main()
