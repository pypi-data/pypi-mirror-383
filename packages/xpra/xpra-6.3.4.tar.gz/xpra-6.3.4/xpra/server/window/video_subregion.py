# This file is part of Xpra.
# Copyright (C) 2013 Antoine Martin <antoine@xpra.org>
# Xpra is released under the terms of the GNU GPL v2, or, at your option, any
# later version. See the file COPYING for details.

import math
from time import monotonic
from typing import Any
from collections.abc import Callable, Sequence

from xpra.os_util import gi_import
from xpra.util.env import envint, envbool
from xpra.util.rectangle import rectangle, add_rectangle, remove_rectangle, merge_all
from xpra.log import Logger

sslog = Logger("regiondetect")
refreshlog = Logger("regionrefresh")

GLib = gi_import("GLib")

VIDEO_SUBREGION = envbool("XPRA_VIDEO_SUBREGION", True)
SUBWINDOW_REGION_BOOST = envint("XPRA_SUBWINDOW_REGION_BOOST", 20)

MAX_TIME = envint("XPRA_VIDEO_DETECT_MAX_TIME", 5)
MIN_EVENTS = envint("XPRA_VIDEO_DETECT_MIN_EVENTS", 20)
MIN_W = envint("XPRA_VIDEO_DETECT_MIN_WIDTH", 128)
MIN_H = envint("XPRA_VIDEO_DETECT_MIN_HEIGHT", 96)

RATIO_WEIGHT = envint("XPRA_VIDEO_DETECT_RATIO_WEIGHT", 80)
KEEP_SCORE = envint("XPRA_VIDEO_DETECT_KEEP_SCORE", 160)


def scoreinout(ww: int, wh: int, region, incount: int, outcount: int) -> int:
    total = incount + outcount
    assert total > 0
    # proportion of damage events that are within this region:
    inregion = incount / total
    # devaluate by taking into account the number of pixels in the area
    # so that a large video region only wins if it really
    # has a larger proportion of the pixels
    # (but also offset this value to even things out a bit:
    # if we have a series of vertical or horizontal bands that we merge,
    # we would otherwise end up excluding the ones on the edge
    # if they ever happen to have a slightly lower hit count)
    # summary: bigger is better, as long as we still have more pixels in than out
    width = min(ww, region.width)
    height = min(wh, region.height)
    # proportion of pixels in this region relative to the whole window:
    inwindow = (width * height) / (ww * wh)
    ratio = inregion / inwindow
    score = 100.0 * inregion
    # if the region has at least 35% of updates, boost it with window ratio
    # (capped at 6, and smoothed with sqrt):
    score += max(0.0, inregion - 0.35) * (math.sqrt(min(6.0, ratio)) - 1.0) * RATIO_WEIGHT
    sslog("scoreinout(%i, %i, %s, %i, %i) inregion=%i%%, inwindow=%i%%, ratio=%.1f, score=%i",
          ww, wh, region, incount, outcount, 100 * inregion, 100 * inwindow, ratio, score)
    return max(0, int(score))


class VideoSubregion:
    def __init__(self, refresh_cb: Callable, auto_refresh_delay: int, supported=False):
        self.refresh_cb = refresh_cb  # usage: refresh_cb(window, regions)
        self.auto_refresh_delay = auto_refresh_delay
        self.supported = supported
        self.enabled = True
        self.detection = True
        self.exclusion_zones: list[rectangle] = []
        self.init_vars()

    def init_vars(self) -> None:
        self.rectangle: rectangle | None = None
        self.inout = 0, 0  # number of damage pixels within / outside the region
        self.score = 0
        self.fps = 0
        self.damaged = 0  # proportion of the rectangle that got damaged (percentage)
        self.set_at = 0  # value of the "damage event count" when the region was set
        self.counter = 0  # value of the "damage event count" recorded at "time"
        self.time: float = 0  # see above
        self.refresh_timer = 0
        self.refresh_regions: list[rectangle] = []
        self.last_scores: dict[rectangle | None, int] = {}
        self.nonvideo_regions: list[rectangle] = []
        self.nonvideo_refresh_timer = 0
        # keep track of how much extra we batch non-video regions (milliseconds):
        self.non_max_wait = 150
        self.min_time = monotonic()

    def reset(self) -> None:
        self.cancel_refresh_timer()
        self.cancel_nonvideo_refresh_timer()
        self.init_vars()

    def cleanup(self) -> None:
        self.reset()

    def __repr__(self):
        return f"VideoSubregion({self.rectangle})"

    def set_enabled(self, enabled: bool) -> None:
        self.enabled = enabled
        if not enabled:
            self.novideoregion("disabled")

    def set_detection(self, detection: bool) -> None:
        self.detection = detection
        if not self.detection:
            self.reset()

    def set_region(self, x: int, y: int, w: int, h: int) -> None:
        sslog("set_region%s", (x, y, w, h))
        if self.detection:
            sslog("video region detection is on - the given region may or may not stick")
        if x == 0 and y == 0 and w == 0 and h == 0:
            self.novideoregion("empty")
        else:
            self.rectangle = rectangle(x, y, w, h)

    def set_exclusion_zones(self, zones) -> None:
        rects = []
        for (x, y, w, h) in zones:
            rects.append(rectangle(int(x), int(y), int(w), int(h)))
        self.exclusion_zones = rects
        # force expire:
        self.counter = 0

    def set_auto_refresh_delay(self, d: int) -> None:
        refreshlog("subregion auto-refresh delay: %s", d)
        if not isinstance(d, int):
            raise ValueError(f"delay is not an int: {d} ({type(d)})")
        self.auto_refresh_delay = d

    def cancel_refresh_timer(self) -> None:
        rt = self.refresh_timer
        refreshlog("%s.cancel_refresh_timer() timer=%s", self, rt)
        if rt:
            self.refresh_timer = 0
            GLib.source_remove(rt)

    def get_info(self) -> dict[str, Any]:
        r = self.rectangle
        info = {
            "supported": self.supported,
            "enabled": self.enabled,
            "detection": self.detection,
            "counter": self.counter,
            "auto-refresh-delay": self.auto_refresh_delay,
        }
        if r is None:
            return info
        info.update({
            "x": r.x,
            "y": r.y,
            "width": r.width,
            "height": r.height,
            "rectangle": (r.x, r.y, r.width, r.height),
            "set-at": self.set_at,
            "time": int(self.time),
            "min-time": int(self.min_time),
            "non-max-wait": self.non_max_wait,
            "timer": self.refresh_timer,
            "nonvideo-timer": self.nonvideo_refresh_timer,
            "in-out": self.inout,
            "score": self.score,
            "fps": self.fps,
            "damaged": self.damaged,
            "exclusion-zones": [(r.x, r.y, r.width, r.height) for r in self.exclusion_zones]
        })
        ls = self.last_scores
        if ls:
            # convert rectangles into tuples:
            info["scores"] = {r.get_geometry(): score for r, score in ls.items() if r is not None}
        rr = tuple(self.refresh_regions)
        if rr:
            for i, r in enumerate(rr):
                info[f"refresh_region[{i}]"] = (r.x, r.y, r.width, r.height)
        nvrr = tuple(self.nonvideo_regions)
        if nvrr:
            for i, r in enumerate(nvrr):
                info[f"nonvideo_refresh_region[{i}]"] = (r.x, r.y, r.width, r.height)
        return info

    def remove_refresh_region(self, region) -> None:
        remove_rectangle(self.refresh_regions, region)
        remove_rectangle(self.nonvideo_regions, region)
        refreshlog("remove_refresh_region(%s) updated refresh regions=%s, nonvideo regions=%s",
                   region, self.refresh_regions, self.nonvideo_regions)

    def add_video_refresh(self, region) -> None:
        # called by add_refresh_region if the video region got painted on
        # Note: this does not run in the UI thread!
        rect = self.rectangle
        if not rect:
            return
        # something in the video region is still refreshing,
        # so we re-schedule the subregion refresh:
        self.cancel_refresh_timer()
        # add the new region to what we already have:
        add_rectangle(self.refresh_regions, region)
        # do refresh any regions which are now outside the current video region:
        # (this can happen when the region moves or changes size)
        nonvideo = []
        for r in self.refresh_regions:
            if not rect.contains_rect(r):
                nonvideo += r.subtract_rect(rect)
        delay = max(150, self.auto_refresh_delay)
        self.nonvideo_regions += nonvideo
        if self.nonvideo_regions:
            if not self.nonvideo_refresh_timer:
                # refresh via timeout_add so this will run in the UI thread:
                self.nonvideo_refresh_timer = GLib.timeout_add(delay, self.nonvideo_refresh)
            # only keep the regions still in the video region:
            inrect = (rect.intersection_rect(r) for r in self.refresh_regions)
            self.refresh_regions = [r for r in inrect if r is not None]
        refreshlog("add_video_refresh(%s) rectangle=%s, delay=%ims, nonvideo=%s, refresh_regions=%s",
                   region, rect, delay, self.nonvideo_regions, self.refresh_regions)
        # re-schedule the video region refresh (if we still have regions to fresh):
        if self.refresh_regions:
            self.refresh_timer = GLib.timeout_add(delay, self.refresh)

    def cancel_nonvideo_refresh_timer(self) -> None:
        nvrt = self.nonvideo_refresh_timer
        refreshlog("cancel_nonvideo_refresh_timer() timer=%s", nvrt)
        if nvrt:
            self.nonvideo_refresh_timer = 0
            GLib.source_remove(nvrt)
            self.nonvideo_regions = []

    def nonvideo_refresh(self) -> None:
        self.nonvideo_refresh_timer = 0
        nonvideo = tuple(self.nonvideo_regions)
        refreshlog("nonvideo_refresh() nonvideo regions=%s", nonvideo)
        if not nonvideo:
            return
        if self.refresh_cb(nonvideo):
            self.nonvideo_regions = []
        # if the refresh didn't fire (refresh_cb() returned False),
        # then we should end up re-scheduling the nonvideo refresh
        # from add_video_refresh()

    def refresh(self) -> None:
        regions = self.refresh_regions
        rect = self.rectangle
        refreshlog("refresh() refresh_timer=%s, refresh_regions=%s, rectangle=%s",
                   self.refresh_timer, regions, rect)
        # runs via timeout_add, safe to call UI!
        self.refresh_timer = 0
        if rect and len(regions) >= 2:
            # figure out if it makes sense to refresh the whole area,
            # or if we just send the list of smaller rectangles:
            pixels = sum(r.width * r.height for r in regions)
            if pixels >= rect.width * rect.height // 2:
                regions = [rect]
        refreshlog("refresh() calling %s with regions=%s", self.refresh_cb, regions)
        if self.refresh_cb(regions):
            self.refresh_regions = []
        else:
            # retry later
            self.refresh_timer = GLib.timeout_add(1000, self.refresh)

    def novideoregion(self, msg, *args) -> None:
        sslog("novideoregion: " + msg, *args)
        self.rectangle = None
        self.time = 0
        self.set_at = 0
        self.counter = 0
        self.inout = 0, 0
        self.score = 0
        self.fps = 0
        self.damaged = 0

    def excluded_rectangles(self, rect, ww: int, wh: int) -> list:
        rects = [rect]
        if self.exclusion_zones:
            for e in self.exclusion_zones:
                new_rects = []
                for r in rects:
                    ex, ey, ew, eh = e.get_geometry()
                    if ex < 0 or ey < 0:
                        # negative values are relative to the width / height of the window:
                        if ex < 0:
                            ex = max(0, ww - ew)
                        if ey < 0:
                            ey = max(0, wh - eh)
                    new_rects += r.subtract(ex, ey, ew, eh)
                rects = new_rects
        return rects

    def identify_video_subregion(self, ww: int, wh: int, damage_events_count, last_damage_events,
                                 starting_at=0.0, children=()):
        if not self.enabled or not self.supported:
            self.novideoregion("disabled")
            return
        from_time: float = 0
        if not self.detection:
            if not self.rectangle:
                return
            # just update the fps:
            from_time = max(starting_at, monotonic() - MAX_TIME, self.min_time)
            self.time = monotonic()
            lde = tuple(x for x in tuple(last_damage_events) if x[0] >= from_time)
            incount = 0
            for _, x, y, w, h in lde:
                r = rectangle(x, y, w, h)
                inregion = r.intersection_rect(self.rectangle)
                if inregion:
                    incount += inregion.width * inregion.height
            elapsed = monotonic() - from_time
            if elapsed <= 0:
                self.fps = 0
            else:
                self.fps = int(incount / (self.rectangle.width * self.rectangle.height) / elapsed)
            return
        sslog("%s.identify_video_subregion(..)", self)
        sslog("identify_video_subregion%s",
              (ww, wh, damage_events_count, last_damage_events, starting_at, children))

        children_rects: Sequence[rectangle] = ()
        if children:
            children_rects = tuple(rectangle(x, y, w, h)
                                   for _xid, x, y, w, h, _border, _depth in children
                                   if w >= MIN_W and h >= MIN_H)

        if damage_events_count < self.set_at:
            # stats got reset
            self.set_at = 0
        # validate against window dimensions:
        rect = self.rectangle
        if rect and (rect.width > ww or rect.height > wh):
            # region is now bigger than the window!
            self.novideoregion("window is now smaller than current region")
            return
        # arbitrary minimum size for regions we will look at:
        # (we don't want video regions smaller than this - too much effort for little gain)
        if ww < MIN_W or wh < MIN_H:
            self.novideoregion("window is too small: %sx%s", MIN_W, MIN_H)
            return

        def update_markers():
            self.counter = damage_events_count
            self.time = monotonic()

        if self.counter + 10 > damage_events_count:
            # less than 10 events since last time we called update_markers:
            elapsed = monotonic() - self.time
            # how many damage events occurred since we chose this region:
            event_count = max(0, damage_events_count - self.set_at)
            # make the timeout longer when the region has worked longer:
            slow_region_timeout = 2 + math.log(2 + event_count, 1.5)
            if rect and elapsed >= slow_region_timeout:
                update_markers()
                self.novideoregion("too much time has passed (%is for %i total events)", elapsed, event_count)
                return
            sslog("identify video: waiting for more damage events (%i) counters: %i / %i",
                  event_count, self.counter, damage_events_count)
            return

        from_time = max(starting_at, monotonic() - MAX_TIME, self.min_time)
        # create a list (copy) to work on:
        lde = tuple(x for x in tuple(last_damage_events) if x[0] >= from_time)
        dc = len(lde)
        if dc <= MIN_EVENTS:
            self.novideoregion("not enough damage events yet (%s)", dc)
            return
        # structures for counting areas and sizes:
        wc: dict[int, dict[int, set[rectangle]]] = {}
        hc: dict[int, dict[int, set[rectangle]]] = {}
        dec: dict[rectangle, int] = {}
        # count how many times we see each area, each width/height and where,
        # after removing any exclusion zones:
        for _, x, y, w, h in lde:
            rects = self.excluded_rectangles(rectangle(x, y, w, h), ww, wh)
            for r in rects:
                dec[r] = dec.get(r, 0) + 1
                if w >= MIN_W:
                    wc.setdefault(w, {}).setdefault(x, set()).add(r)
                if h >= MIN_H:
                    hc.setdefault(h, {}).setdefault(y, set()).add(r)
        # we can shortcut the damaged ratio if the whole window got damaged at least once:
        all_damaged = dec.get(rectangle(0, 0, ww, wh), 0) > 0

        def inoutcount(region, ignore_size=0):
            # count how many pixels are in or out if this region
            incount, outcount = 0, 0
            for r, count in dec.items():
                inregion = r.intersection_rect(region)
                if inregion:
                    incount += inregion.width * inregion.height * int(count)
                outregions = r.subtract_rect(region)
                for x in outregions:
                    if ignore_size > 0 and x.width * x.height < ignore_size:
                        # skip small region outside rectangle
                        continue
                    outcount += x.width * x.height * int(count)
            return incount, outcount

        def damaged_ratio(rect: rectangle):
            if all_damaged:
                return 1
            rects: list[rectangle] = [rect, ]
            for _, x, y, w, h in lde:
                r = rectangle(x, y, w, h)
                new_rects = []
                for cr in rects:
                    new_rects += cr.subtract_rect(r)
                if not new_rects:
                    # nothing left: damage covered the whole rect
                    return 1.0
                rects = new_rects
            not_damaged_pixels = sum((r.width * r.height) for r in rects)
            rect_pixels = rect.width * rect.height
            # sslog("damaged_ratio: not damaged pixels(%s)=%i, rect pixels(%s)=%i",
            #     rects, not_damaged_pixels, rect, rect_pixels)
            return max(0, min(1, 1.0 - not_damaged_pixels / rect_pixels))

        scores = {None: 0}

        def score_region(info: str, region: rectangle, ignore_size=0, d_ratio=0.0) -> int:
            score = scores.get(region)
            if score is not None:
                return score

            def rec(score: int):
                scores[region] = score
                return score

            # check if the region given is a good candidate, and if so we use it
            # clamp it:
            if region.width < MIN_W or region.height < MIN_H:
                # too small, ignore it:
                sslog(f"region too small: {region.width}x{region.height}")
                return rec(0)
            # and make sure this does not end up much bigger than needed:
            if ww * wh < (region.width * region.height):
                sslog(f"region too small: {region.width}x{region.height}")
                return rec(0)
            incount, outcount = inoutcount(region, ignore_size)
            total = incount + outcount
            children_boost = 0
            if total == 0:
                ipct = opct = score = 0
            else:
                ipct = 100 * incount // total
                opct = 100 * outcount // total
            if score is None:
                score = scoreinout(ww, wh, region, incount, outcount)
                # discount score if the region contains areas that were not damaged:
                # (apply sqrt to limit the discount: 50% damaged -> multiply by 0.7)
                if d_ratio == 0:
                    d_ratio = damaged_ratio(region)
                score = int(score * math.sqrt(d_ratio))
                children_boost = int(region in children_rects) * SUBWINDOW_REGION_BOOST
            sslog("testing %12s video region %34s: "
                  "%3i%% in, %3i%% out, %3i%% of window, damaged ratio=%.2f, children_boost=%i, score=%2i",
                  info, region, ipct, opct, 100 * region.width * region.height / ww / wh, d_ratio, children_boost,
                  score)
            return rec(score)

        def updateregion(rect: rectangle) -> None:
            self.rectangle = rect
            self.time = monotonic()
            self.inout = inoutcount(rect)
            self.score = scoreinout(ww, wh, rect, *self.inout)
            elapsed = monotonic() - from_time
            if elapsed <= 0:
                self.fps = 0
            else:
                self.fps = int(self.inout[0] / (rect.width * rect.height) / elapsed)
            self.damaged = int(100 * damaged_ratio(self.rectangle))
            self.last_scores = scores
            sslog("score(%s)=%s, damaged=%i%%", self.inout, self.score, self.damaged)

        def setnewregion(rect: rectangle, msg: str, *args) -> None:
            rects = self.excluded_rectangles(rect, ww, wh)
            if not rects:
                self.novideoregion("no match after removing excluded regions")
                return
            if len(rects) == 1:
                rect = rects[0]
            else:
                # use the biggest one of what remains:
                def get_rect_size(rect):
                    return -rect.width * rect.height

                biggest_rects = sorted(rects, key=get_rect_size)
                rect = biggest_rects[0]
                if rect.width < MIN_W or rect.height < MIN_H:
                    self.novideoregion("match is too small after removing excluded regions")
                    return
            if not self.rectangle or self.rectangle != rect:
                sslog("setting new region %s: " + msg, rect, *args)
                sslog(" is child window: %s", rect in children_rects)
                self.set_at = damage_events_count
                self.counter = damage_events_count
            if not self.enabled:
                # could have been disabled since we started this method!
                self.novideoregion("disabled")
                return
            if not self.detection:
                return
            updateregion(rect)

        update_markers()

        if len(dec) == 1:
            rect, count = tuple(dec.items())[0]
            setnewregion(rect, "only region damaged")
            return

        # see if we can keep the region we already have (if any):
        cur_score = 0
        if rect:
            cur_score = score_region("current", rect)
            if cur_score >= KEEP_SCORE:
                sslog("keeping existing video region %s with score %s", rect, cur_score)
                return

        # split the regions we really care about (enough pixels, big enough):
        damage_count = {}
        min_count = max(2, len(lde) // 40)
        for r, count in dec.items():
            # ignore small regions:
            if count > min_count and r.width >= MIN_W and r.height >= MIN_H:
                damage_count[r] = count
        c = sum(int(x) for x in damage_count.values())
        if c > 0:
            most_damaged = int(sorted(damage_count.values())[-1])
            most_pct = round(100 * most_damaged / c)
            sslog("identify video: most=%s%% damage count=%s", most_pct, damage_count)
            # is there a region that stands out?
            # try to use the region which is responsible for most of the large damage requests:
            most_damaged_regions = tuple(r for r, v in damage_count.items() if v == most_damaged)
            if len(most_damaged_regions) == 1:
                r = most_damaged_regions[0]
                score = score_region("most-damaged", r, d_ratio=1.0)
                sslog(f"identify video: score most damaged area {r}={score}%")
                if score > 120:
                    setnewregion(r, f"{most_pct}% of large damage requests, {score=}")
                    return
                if score >= 100:
                    scores[r] = score

        # try children windows:
        for region in children_rects:
            scores[region] = score_region("child-window", region, 48 * 48)

        # try harder: try combining regions with the same width or height:
        # (some video players update the video region in bands)
        for w, d in wc.items():
            for x, regions in d.items():
                if len(regions) >= 2:
                    # merge regions of width w at x
                    min_count = max(2, len(regions) // 25)
                    keep = tuple(r for r in regions if int(dec.get(r, 0)) >= min_count)
                    sslog("vertical regions of width %i at %i with at least %i hits: %s", w, x, min_count, keep)
                    if keep:
                        merged = merge_all(keep)
                        scores[merged] = score_region("vertical", merged, 48 * 48)
        for h, d in hc.items():
            for y, regions in d.items():
                if len(regions) >= 2:
                    # merge regions of height h at y
                    min_count = max(2, len(regions) // 25)
                    keep = tuple(r for r in regions if int(dec.get(r, 0)) >= min_count)
                    sslog("horizontal regions of height %i at %i with at least %i hits: %s", h, y, min_count, keep)
                    if keep:
                        merged = merge_all(keep)
                        scores[merged] = score_region("horizontal", merged, 48 * 48)

        sslog("merged regions scores: %s", scores)
        highscore = max(scores.values())
        # a score of 100 is neutral
        if highscore >= 120:
            region = next(iter(r for r, s in scores.items() if s == highscore))
            setnewregion(region, "very high score: %s", highscore)
            return

        # retry existing region, tolerate lower score:
        if cur_score >= 90 and (highscore < 100 or cur_score >= highscore):
            sslog("keeping existing video region %s with score %s", rect, cur_score)
            setnewregion(self.rectangle, f"existing region with score: {cur_score}")
            return

        if highscore >= 100:
            region = next(iter(r for r, s in scores.items() if s == highscore))
            setnewregion(region, "high score: %s", highscore)
            return

        # could do:
        # * re-add some scrolling detection: the region may have moved
        # * re-try with a higher "from_time" and a higher score threshold

        # try harder still: try combining all the regions we haven't discarded
        # (Flash player with Firefox and Youtube does stupid unnecessary repaints)
        if len(damage_count) >= 2:
            merged = merge_all(tuple(damage_count.keys()))
            score = score_region("merged", merged)
            if score >= 110:
                setnewregion(merged, "merged all regions, score=%s", score)
                return

        self.novideoregion("failed to identify a video region")
        self.last_scores = scores
