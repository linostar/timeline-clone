# Copyright (C) 2009, 2010, 2011  Rickard Lindberg, Roger Lindberg
#
# This file is part of Timeline.
#
# Timeline is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Timeline is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Timeline.  If not, see <http://www.gnu.org/licenses/>.


import os
import getpass


from timelinelib.db.exceptions import TimelineIOError
from timelinelib.wxgui.utils import get_user_ack
from timelinelib.wxgui.utils import display_warning_message


class LockedException(Exception):
    pass


class TimelineApplication(object):

    def __init__(self, main_frame, db_open_fn, config):
        self.main_frame = main_frame
        self.db_open_fn = db_open_fn
        self.config = config
        self.timeline = None

    def on_started(self, application_arguments):
        input_files = application_arguments.get_files()
        if len(input_files) == 0:
            ro = self.config.get_recently_opened()
            if self.config.get_open_recent_at_startup() and len(ro) > 0:
                self.main_frame.open_timeline_if_exists(ro[0])
        else:
            for input_file in input_files:
                self.main_frame.open_timeline(input_file)

    def open_timeline(self, path):
        try:
            self.timeline = self.db_open_fn(path, self.config.get_use_wide_date_range())
        except TimelineIOError, e:
            self.main_frame.handle_db_error(e)
            self.timelinepath = None
        else:
            self.config.append_recently_opened(path)
            self.main_frame._update_open_recent_submenu()
            self.main_frame._display_timeline(self.timeline)
            self.timelinepath = path
            self.last_changed = self._get_modification_date()

    def set_no_timeline(self):
        self.timeline = None
        self.main_frame._display_timeline(None)

    def on_play_clicked(self):
        self.main_frame.open_play_frame(self.timeline)
        
    def set_timeline_in_readonly_mode(self):
        try:
            self.timeline.set_readonly()
            self.main_frame.timeline_is_readonly()
        except:
            pass
        
    def ok_to_edit(self):
        if self.timeline.is_read_only():
            return False
        if self._locked():
            display_warning_message("The Timeline is Locked by someone else.\nTry again later")
            return False
        if self._timeline_path_doesnt_exists_yet():
            self._lock()
            return True
        last_changed = self._get_modification_date()
        if last_changed > self.last_changed:
            ack = get_user_ack(_("Someoneelse has changed the Timeline.\nYou have two choices!\n  1. Set Timeline in Read-Only mode.\n  2. Synchronize Timeline.\n\nDo you want to Synchronize?"))
            if ack:
                self._synchronize()
            else:
                self.set_timeline_in_readonly_mode()
            return False
        if last_changed > 0:
            self._lock()
        return True
    
    def _timeline_path_doesnt_exists_yet(self):
        return not os.path.exists(self.timelinepath)
        
    def edit_ends(self):
        if self.timeline is not None:
            if self._the_lock_is_mine():
                self.last_changed = self._get_modification_date()
                self._unlock()
        
    def _get_modification_date(self):
        try:
            return os.path.getmtime(self.timelinepath)
        except:
            return 0
    
    def _synchronize(self):
        drawing_area = self.main_frame.main_panel.timeline_panel.drawing_area
        vp = drawing_area.get_view_properties()
        displayed_period = vp.get_displayed_period()
        self.open_timeline(self.timelinepath)
        vp.set_displayed_period(displayed_period) 
        drawing_area.redraw_timeline()

    def _lock(self):
        fp = None
        try:
            ts = self._get_timestamp_string()
            path = self._get_lockpath()
            fp = open(path, "w")
            fp.write("%s\n%s\n%s" % (getpass.getuser(), ts, os.getpid()))
        except Exception, ex:
            print ex
            raise LockedException("Unable to take lock on %s" % self.timelinepath)
        finally:
            if fp is not None:
                fp.close()
                
    def _get_lockpath(self):
        return "%s.lock" % self.timelinepath

    def _get_timestamp_string(self):
        now = self.timeline.time_type.now()
        return self.timeline.time_type.time_string(now)

    def _locked(self):
        lockpath = self._get_lockpath()
        return os.path.exists(lockpath)
    
    def _unlock(self):
        lockpath = self._get_lockpath()
        if os.path.exists(lockpath):
            os.remove(lockpath)

    def _the_lock_is_mine(self):
        fp = None
        try:
            user = getpass.getuser()
            pid = os.getpid()
            lockpath = self._get_lockpath()
            fp = open(lockpath, "r")
            lines = fp.readlines()
            lines = [line.strip() for line in lines]
            return lines[0] == user and lines[2] == "%s" % pid
        except:
            return False
        finally:
            if fp is not None:
                fp.close()
