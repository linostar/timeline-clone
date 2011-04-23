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


import os.path
import shutil
import sys
import tempfile
import traceback
import unittest

from timelinelib.arguments import ApplicationArguments
from timelinelib.config import read_config
from timelinelib.gui.setup import start_wx_application

import wx
import wx.lib.inspection


class EndToEndTestCase(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="timeline-test")
        self.config_file_path = os.path.join(self.tmp_dir, "thetimelineproj.cfg")
        self.config = read_config(self.config_file_path)
        self.standard_excepthook = sys.excepthook
        self.error_in_gui_thread = None

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)
        sys.excepthook = self.standard_excepthook

    def start_timeline_and(self, steps_to_perform_in_gui):
        self.config.write()
        self.steps_to_perform_in_gui = steps_to_perform_in_gui
        application_arguments = ApplicationArguments()
        application_arguments.parse_from(
            ["--config-file", self.config_file_path, ":tutorial:"])
        start_wx_application(application_arguments, self._before_main_loop_hook)
        if self.error_in_gui_thread:
            exc_type, exc_value, exc_traceback = self.error_in_gui_thread
            a = traceback.format_exception(exc_type, exc_value, exc_traceback)
            self.fail("Exception in GUI thread: %s" % "".join(a))

    def _before_main_loop_hook(self):
        sys.excepthook = self.standard_excepthook
        self._setup_steps_to_perform_in_gui(self.steps_to_perform_in_gui)

    def _setup_steps_to_perform_in_gui(self, steps, in_sub_step_mode=False):
        def perform_current_step_and_queue_next():
            if len(steps) >= 2 and isinstance(steps[1], list):
                self._setup_steps_to_perform_in_gui(steps[1], True)
                next_step_index = 2
            else:
                next_step_index = 1
            try:
                steps[0]()
            except Exception:
                wx.GetApp().ExitMainLoop()
                self.error_in_gui_thread = sys.exc_info()
            else:
                if steps[0] != self.show_widget_inspector:
                    self._setup_steps_to_perform_in_gui(steps[next_step_index:], in_sub_step_mode)
        if len(steps) > 0:
            wx.CallAfter(perform_current_step_and_queue_next)
        elif not in_sub_step_mode:
            wx.GetApp().ExitMainLoop()

    def show_widget_inspector(self):
        wx.lib.inspection.InspectionTool().Show()

    def find_component(self, component_path):
        components_to_search_in = wx.GetTopLevelWindows()
        for part in component_path.split("."):
            component = self._find_component_with_name_in(components_to_search_in, part)
            if component == None:
                self.fail("Could not find component with path '%s'." % component_path)
            else:
                components_to_search_in = component.GetChildren()
        return component

    def _find_component_with_name_in(self, components, seeked_name):
        for component in components:
            if component.GetName() == seeked_name:
                return component
        for component in components:
            sub = self._find_component_with_name_in(component.GetChildren(), seeked_name)
            if sub:
                return sub
        return None
