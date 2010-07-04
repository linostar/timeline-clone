# Copyright (C) 2009, 2010  Rickard Lindberg, Roger Lindberg
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


"""
Script that runs all automated tests whenever a file changes on disk.

To run this script:

    python gui-test-runner.py --test

To run this script with itself:

    python gui-test-runner.py --test-bootstrap

It currently only works on Linux since it relies on the pyinotify module to
watch the file system for changes.
"""


import sys
import os.path
import unittest
import subprocess

import wx
from mock import Mock


class CommandRunnerView(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, size=(400, 400))
        self._create_gui()
        self.controller = CommandRunnerController(self)
        self.start_poll_timer()

    def configure(self, dir, command):
        self.controller.configure(dir, command)

    def clear_output(self):
        self.output_ctrl.Clear()

    def append_output(self, output):
        self.output_ctrl.AppendText(output)

    def set_running_state(self):
        self.status_button.SetBackgroundColour((200, 200, 0))
        self.status_button.SetLabel("RUNNING...")

    def set_success_state(self):
        self.status_button.SetBackgroundColour((0, 200, 0))
        self.status_button.SetLabel("SUCCESS")

    def set_error_state(self):
        self.status_button.SetBackgroundColour((200, 0, 0))
        self.status_button.SetLabel("FAILURE")

    def start_wait_timer(self):
        self.wait_timer.Start(milliseconds=1000, oneShot=True)

    def start_poll_timer(self):
        self.poll_timer.Start(milliseconds=500)

    def _create_gui(self):
        # Controls
        wrap_panel = wx.Panel(self)
        self.status_button = wx.Button(wrap_panel, size=(-1, 70))
        self.output_ctrl = wx.TextCtrl(wrap_panel, style=wx.TE_MULTILINE|wx.TE_READONLY)
        font = wx.Font(10, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        style = wx.TextAttr((0, 0, 0), font=font)
        self.output_ctrl.SetDefaultStyle(style)
        # Timers
        self.wait_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._wait_timer_on_tick, self.wait_timer)
        self.poll_timer = wx.Timer(self)
        # Bindings
        self.Bind(wx.EVT_TIMER, self._poll_timer_on_tick, self.poll_timer)
        self.Bind(wx.EVT_BUTTON, self._btn_status_on_click, self.status_button)
        # Create layout with sizers
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.status_button, flag=wx.GROW, proportion=0)
        sizer.Add(self.output_ctrl, flag=wx.GROW, proportion=1)
        wrap_panel.SetSizer(sizer)

    def _btn_status_on_click(self, evt):
        self.controller.start()

    def _wait_timer_on_tick(self, evt):
        self.controller.end()

    def _poll_timer_on_tick(self, evt):
        self.controller.poll()


class CommandRunnerController(object):

    def __init__(self, view):
        self.view = view
        self.command_runner = None
        self.watcher = None

    def set_command_runner(self, command_runner):
        self.command_runner = command_runner

    def set_watcher(self, watcher):
        self.watcher = watcher

    def configure(self, dir, command):
        self.set_command_runner(CommandRunner(self.view, command))
        self.set_watcher(PyinotifyWatcher(dir, self))
        self.run_command()

    def run_command(self):
        self.start()

    def start(self):
        if not self.command_runner:
            raise Exception("Can't run without command runner configured.")
        self.command_runner.start()
        self.view.start_wait_timer()

    def end(self):
        if not self.command_runner:
            raise Exception("Can't run without command runner configured.")
        self.command_runner.end()

    def poll(self):
        if self.watcher:
            self.watcher.poll()


class CommandRunner(object):

    def __init__(self, view, command_str):
        self.view = view
        self.command_str = command_str
        self.process = None

    def is_running(self):
        return self.process != None

    def start(self):
        self.process = self._create_popen_from_command_str()
        self.view.clear_output()
        self.view.set_running_state()
        self.view.append_output("> %s\n" % self.command_str)

    def end(self):
        if not self.is_running():
            raise Exception("Can't call end before start.")
        retcode = self.process.wait()
        output = self.process.stdout.read()
        if retcode == 0:
            self.view.set_success_state()
        else:
            self.view.set_error_state()
        self.view.append_output(output)
        self.process = None

    def _create_popen_from_command_str(self):
        return subprocess.Popen(self.command_str.split(" "),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)


class PyinotifyWatcher(object):

    def __init__(self, dir, controller):
        self.dir = dir
        self.controller = controller
        self._setup_pyionotify()

    def poll(self):
        self.notifier.process_events()
        while self.notifier.check_events():  #loop in case more events appear while we are processing
              self.notifier.read_events()
              self.notifier.process_events()

    def _setup_pyionotify(self):
        import pyinotify
        wm = pyinotify.WatchManager()  # Watch Manager
        class EventHandler(pyinotify.ProcessEvent):
            def __init__(self, controller):
                self.controller = controller
            def process_IN_MODIFY(self, event):
                if event.pathname.endswith(".swp"):
                    return
                self.controller.run_command()
        handler = EventHandler(self.controller)
        notifier = pyinotify.Notifier(wm, handler, timeout=10)
        wdd = wm.add_watch(self.dir, pyinotify.ALL_EVENTS, rec=True,
                           auto_add=True)
        self.notifier = notifier


def configure_run_timeline(view):
    dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    path_to_script = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "tests", "run.py"))
    command = "python %s" % path_to_script
    view.configure(dir, command)


def configure_run_self(view):
    dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    command = "python %s --test" % os.path.join(os.path.dirname(__file__), "gui-test-runner.py")
    view.configure(dir, command)


def main():
    app = wx.PySimpleApp()
    view = CommandRunnerView()
    view.Show()
    if "--test-bootstrap" in sys.argv:
        configure_run_self(view)
    else:
        configure_run_timeline(view)
    app.MainLoop()


class TestCommandRunnerController(unittest.TestCase):

    def setUp(self):
        self.view = Mock()
        self.controller = CommandRunnerController(self.view)

    def testStartWithoutCommand(self):
        self.assertRaises(Exception, self.controller.start)

    def testStart(self):
        command_runner = Mock()
        self.controller.set_command_runner(command_runner)
        self.controller.start()
        self.assertTrue(command_runner.start.called)
        self.assertTrue(self.view.start_wait_timer.called)

    def testEndWithoutCommand(self):
        self.assertRaises(Exception, self.controller.end)

    def testEnd(self):
        command_runner = Mock()
        self.controller.set_command_runner(command_runner)
        self.controller.end()
        self.assertTrue(command_runner.end.called)

    def testPoll(self):
        self.controller.poll()
        watcher = Mock()
        self.controller.set_watcher(watcher)
        self.controller.poll()
        self.assertTrue(watcher.poll.called)


class TestCommandRunner(unittest.TestCase):

    def setUp(self):
        self.view = Mock()
        self.popen = Mock()
        self.runner = CommandRunner(self.view, "ls")
        self.runner._create_popen_from_command_str = lambda: self.popen

    def testStart(self):
        self.assertFalse(self.runner.is_running())
        self.runner.start()
        self.assertTrue(self.runner.is_running())
        self.assertTrue(self.view.set_running_state.called)
        self.assertTrue(self.view.clear_output.called)

    def testEndBeforeStart(self):
        self.assertRaises(Exception, self.runner.end)

    def testEndWithError(self):
        self.popen.wait.return_value = 1
        self.popen.stdout.read.return_value = "foo"
        self.runner.start()
        self.runner.end()
        self.assertTrue(self.view.set_error_state.called)
        self.view.append_output.assert_called_with("foo")
        self.assertFalse(self.runner.is_running())

    def testEndWithSuccess(self):
        self.popen.wait.return_value = 0
        self.popen.stdout.read.return_value = "foo"
        self.runner.start()
        self.runner.end()
        self.assertTrue(self.view.set_success_state.called)
        self.view.append_output.assert_called_with("foo")
        self.assertFalse(self.runner.is_running())


class TestFileSystemWatcher(unittest.TestCase):

    def setUp(self):
        self.controller = Mock()
        self.watcher = PyinotifyWatcher(".", self.controller)


if __name__ == '__main__':
    if "--test" in sys.argv:
        # Remove this switch since the unittest.main method is otherwise
        # confused
        sys.argv.remove("--test")
        unittest.main()
    else:
        main()
