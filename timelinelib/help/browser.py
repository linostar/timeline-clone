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


from timelinelib.gui.dialogs.helpbrowser import HelpBrowser
from timelinelib.gui.utils import _display_error_message
from timelinelib.paths import HELP_RESOURCES_DIR


class HelpBrowserController(object):

    def __init__(self, parent):
        self.parent = parent
        self._create_browser()

    def _create_browser(self):
        try:
            import markdown
        except ImportError:
            self.help_browser = None
        else:
            import timelinelib.help.system as help
            import timelinelib.help.pages as help_pages
            help_system = help.HelpSystem("contents", HELP_RESOURCES_DIR + "/",
                                          "page:")
            help_pages.install(help_system)
            self.help_browser = HelpBrowser(self.parent, help_system)

    def show_help_page(self, page):
        if self.help_browser is None:
            _display_error_message(
                _("Could not find markdown Python package.  It is needed by the help system. See the Timeline website or the INSTALL file for instructions how to install it."),
                self.parent)
        else:
            self.help_browser.show_page(page)
