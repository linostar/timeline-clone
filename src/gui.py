# Copyright (C) 2009  Rickard Lindberg, Roger Lindberg
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
GUI components.

The GUI components are mainly for interacting with the user and should not
contain much logic. For example, the drawing algorithm is responsible for
drawing the timeline, but the `DrawingArea` class in this module provides the
GUI component on which it will draw.
"""


import datetime
import calendar
import logging
import os.path
from datetime import datetime as dt
from datetime import time

import wx
import wx.html
import wx.lib.colourselect as colourselect
from wx.lib.masked import TimeCtrl

from data import Timeline
from data import Event
from data import Category
from data import TimePeriod
import data
import drawing
import config
from about import display_about_dialog
from about import APPLICATION_NAME
from paths import ICONS_DIR
from paths import MANUAL_FILE
from paths import HELP_RESOURCES_DIR
import help
import help_pages


# Border, in pixels, between controls in a window (should always be used when
# border is needed)
BORDER = 5


help_browser = None


class MainFrame(wx.Frame):
    """
    The main frame of the application.

    Can be resized, maximized and minimized. The frame contains one panel.

    Owns an instance of a timeline that is currently being displayed. When the
    timeline changes, this control will notify sub controls about it.
    """

    def __init__(self):
        wx.Frame.__init__(self, None, size=config.get_window_size(),
                          style=wx.DEFAULT_FRAME_STYLE)
        # To enable translations of wx stock items.
        self.locale = wx.Locale(wx.LANGUAGE_DEFAULT)
        self._set_initial_values_to_member_variables()
        self._create_gui()
        self.Maximize(config.get_window_maximized())
        self.SetTitle(APPLICATION_NAME)
        self.mnu_view_sidebar.Check(config.get_show_sidebar())
        self.mnu_view_legend.Check(config.get_show_legend())
        self._enable_disable_menus()
        self.SetIcons(self._load_icon_bundle())
        self._init_help_system()

    def display_timeline(self, input_file):
        """Read timeline info from the given input file and display it."""
        def error_fn(msg):
            _display_error_message(msg, self)
        try:
            self.timeline = data.get_timeline(input_file, error_fn)
        except Exception, e:
            msg_template = _("Unable to open timeline '%s'.") + "\n\n%s"
            _display_error_message(msg_template % (input_file, e))
        else:
            self.SetTitle("%s (%s) - %s" % (os.path.basename(input_file),
                                            os.path.dirname(os.path.abspath(input_file)),
                                            APPLICATION_NAME))
            # Notify sub controls that we have a new timeline
            self.main_panel.catbox.set_timeline(self.timeline)
            self.main_panel.drawing_area.set_timeline(self.timeline)
        self._enable_disable_menus()

    def _create_gui(self):
        def add_ellipses_to_menuitem(id):
            plain = wx.GetStockLabel(id,
                    wx.STOCK_WITH_ACCELERATOR|wx.STOCK_WITH_MNEMONIC)
            # format of plain 'xxx[\tyyy]', example '&New\tCtrl+N'
            tab_index = plain.find("\t")
            if tab_index != -1:
                return plain[:tab_index] + "..." + plain[tab_index:]
            return plain + "..."
        # The only content of this frame is the MainPanel
        self.main_panel = MainPanel(self)
        self.Bind(wx.EVT_CLOSE, self._window_on_close)
        # The status bar
        self.CreateStatusBar()
        # The menu
        # File menu
        self.mnu_file = wx.Menu()
        self.mnu_file.Append(wx.ID_NEW, add_ellipses_to_menuitem(wx.ID_NEW),
                             _("Create a new timeline"))
        self.mnu_file.Append(wx.ID_OPEN, add_ellipses_to_menuitem(wx.ID_OPEN),
                             _("Open an existing timeline"))
        self.mnu_file.AppendSeparator()
        self.mnu_file_export = self.mnu_file.Append(wx.ID_ANY,
                                                    _("&Export to Image..."),
                                                    _("Export the current view to a PNG image"))
        self.mnu_file.AppendSeparator()
        self.mnu_file.Append(wx.ID_EXIT, "",
                             _("Exit the program"))
        self.Bind(wx.EVT_MENU, self._mnu_file_new_on_click, id=wx.ID_NEW)
        self.Bind(wx.EVT_MENU, self._mnu_file_open_on_click, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self._mnu_file_export_on_click,
                  self.mnu_file_export)
        self.Bind(wx.EVT_MENU, self._mnu_file_exit_on_click, id=wx.ID_EXIT)
        # Timeline menu
        self.mnu_timeline = wx.Menu()
        mnu_timeline_create_event = self.mnu_timeline.Append(wx.ID_ANY,
                                    _("Create &Event..."),
                                    _("Create a new event"))
        mnu_timeline_edit_categories = self.mnu_timeline.Append(wx.ID_ANY,
                                       _("Edit &Categories"),
                                       _("Edit categories"))
        self.Bind(wx.EVT_MENU, self._mnu_timeline_create_event_on_click,
                  mnu_timeline_create_event)
        self.Bind(wx.EVT_MENU, self._mnu_timeline_edit_categories_on_click,
                  mnu_timeline_edit_categories)
        # View menu
        self.mnu_view = wx.Menu()
        self.mnu_view_sidebar = self.mnu_view.Append(wx.ID_ANY,
                                                     _("&Sidebar\tCtrl+I"),
                                                     kind=wx.ITEM_CHECK)
        self.mnu_view_legend = self.mnu_view.Append(wx.ID_ANY,
                                                    _("&Legend"),
                                                    kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self._mnu_view_sidebar_on_click,
                  self.mnu_view_sidebar)
        self.Bind(wx.EVT_MENU, self._mnu_view_legend_on_click,
                  self.mnu_view_legend)
        # Navigate menu
        self.mnu_navigate = wx.Menu()
        goto_today = self.mnu_navigate.Append(wx.ID_ANY, _("Go to &Today\tCtrl+H"))
        goto_date = self.mnu_navigate.Append(wx.ID_ANY, _("Go to D&ate...\tCtrl+G"))
        self.mnu_navigate.AppendSeparator()
        backward = self.mnu_navigate.Append(wx.ID_ANY, _("Backward\tPgUp"))
        forward = self.mnu_navigate.Append(wx.ID_ANY, _("Forward\tPgDn"))
        self.mnu_navigate.AppendSeparator()
        fit_year = self.mnu_navigate.Append(wx.ID_ANY, _("Fit Year"))
        fit_month = self.mnu_navigate.Append(wx.ID_ANY, _("Fit Month"))
        fit_day = self.mnu_navigate.Append(wx.ID_ANY, _("Fit Day"))
        self.Bind(wx.EVT_MENU, self._mnu_navigate_goto_today_on_click, goto_today)
        self.Bind(wx.EVT_MENU, self._mnu_navigate_goto_date_on_click, goto_date)
        self.Bind(wx.EVT_MENU, self._mnu_navigate_backward_on_click, backward)
        self.Bind(wx.EVT_MENU, self._mnu_navigate_forward_on_click, forward)
        self.Bind(wx.EVT_MENU, self._mnu_navigate_fit_year_on_click, fit_year)
        self.Bind(wx.EVT_MENU, self._mnu_navigate_fit_month_on_click, fit_month)
        self.Bind(wx.EVT_MENU, self._mnu_navigate_fit_day_on_click, fit_day)
        # Help menu
        self.mnu_help = wx.Menu()
        help_contents = self.mnu_help.Append(wx.ID_HELP, _("&Contents\tF1"))
        self.Bind(wx.EVT_MENU, self._mnu_help_contents_on_click, help_contents)
        self.mnu_help.AppendSeparator()
        help_tutorial = self.mnu_help.Append(wx.ID_ANY, _("Getting started tutorial"))
        self.Bind(wx.EVT_MENU, self._mnu_help_tutorial_on_click, help_tutorial)
        help_contact = self.mnu_help.Append(wx.ID_ANY, _("Contact us"))
        self.Bind(wx.EVT_MENU, self._mnu_help_contact_on_click, help_contact)
        self.mnu_help.AppendSeparator()
        help_about = self.mnu_help.Append(wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self._mnu_help_about_on_click, help_about)
        # The menu bar
        menuBar = wx.MenuBar()
        menuBar.Append(self.mnu_file, _("&File"))
        menuBar.Append(self.mnu_view, _("&View"))
        menuBar.Append(self.mnu_timeline, _("&Timeline"))
        menuBar.Append(self.mnu_navigate, _("&Navigate"))
        menuBar.Append(self.mnu_help, _("&Help"))
        self.SetMenuBar(menuBar)

    def _window_on_close(self, event):
        self._save_current_timeline_data()
        self._save_application_config()
        self.Destroy()

    def _mnu_file_new_on_click(self, event):
        """Event handler used when the user wants to create a new timeline."""
        self._create_new_timeline()

    def _mnu_file_open_on_click(self, event):
        """Event handler used when the user wants to open a new timeline."""
        self._open_existing_timeline()

    def _mnu_file_export_on_click(self, evt):
        self._export_to_image()

    def _mnu_file_exit_on_click(self, evt):
        """Event handler for the Exit menu item"""
        self.Close()

    def _mnu_view_sidebar_on_click(self, evt):
        if evt.IsChecked():
            self.main_panel.show_sidebar()
        else:
            self.main_panel.hide_sidebar()

    def _mnu_view_legend_on_click(self, evt):
        self.main_panel.drawing_area.show_hide_legend(evt.IsChecked())

    def _mnu_timeline_create_event_on_click(self, evt):
        """Event handler for the New Event menu item"""
        _create_new_event(self.timeline)

    def _mnu_timeline_edit_categories_on_click(self, evt):
        """Event handler for the Edit Categories menu item"""
        _edit_categories(self.timeline)

    def _mnu_navigate_goto_today_on_click(self, evt):
        self._navigate_timeline(lambda tp: tp.center(dt.now()))

    def _mnu_navigate_goto_date_on_click(self, evt):
        self._goto_date()

    def _mnu_navigate_backward_on_click(self, evt):
        self._navigate_backward()

    def _mnu_navigate_forward_on_click(self, evt):
        self._navigate_forward()

    def _mnu_navigate_fit_year_on_click(self, evt):
        self._navigate_timeline(lambda tp: tp.fit_year())

    def _mnu_navigate_fit_month_on_click(self, evt):
        self._navigate_timeline(lambda tp: tp.fit_month())

    def _mnu_navigate_fit_day_on_click(self, evt):
        self._navigate_timeline(lambda tp: tp.fit_day())

    def _mnu_help_contents_on_click(self, e):
        help_browser.show_page("contents")

    def _mnu_help_tutorial_on_click(self, e):
        help_browser.show_page("tutorial")

    def _mnu_help_contact_on_click(self, e):
        help_browser.show_page("contact")

    def _mnu_help_about_on_click(self, e):
        display_about_dialog()

    def _init_help_system(self):
        help_system = help.HelpSystem("contents", HELP_RESOURCES_DIR + "/", "page:")
        help_pages.install(help_system)
        global help_browser
        help_browser = HelpBrowser(self, help_system)

    def _create_new_timeline(self):
        """
        Create a new empty timeline.

        The user is asked to enter the filename of the new timeline to be
        created.

        If the new filename entered, should already exist, the existing
        timeline is opened. The user will be informed about this situation.
        """
        dialog = wx.FileDialog(self, message=_("Create Timeline"),
                               wildcard=self.wildcard, style=wx.FD_SAVE)
        if dialog.ShowModal() == wx.ID_OK:
            self._save_current_timeline_data()
            path, extension = _extend_path(dialog.GetPath(), self.extensions,
                                           self.default_extension)
            if os.path.exists(path):
                msg_first_part = _("The specified timeline already exists.")
                msg_second_part = _("Opening timeline instead of creating new.")
                wx.MessageBox("%s\n\n%s" % (msg_first_part, msg_second_part),
                              _("Information"),
                              wx.OK|wx.ICON_INFORMATION, self)
            self.display_timeline(path)
        dialog.Destroy()

    def _open_existing_timeline(self):
        """
        Open a new timeline.

        The user is asked to enter the filename of the timeline to be opened.
        """
        dialog = wx.FileDialog(self, message=_("Open Timeline"),
                               wildcard=self.wildcard, style=wx.FD_OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            self._save_current_timeline_data()
            self.display_timeline(dialog.GetPath())
        dialog.Destroy()

    def _enable_disable_menus(self):
        """
        Enable or disable menu items depending on the state of the application.
        """
        menues = [self.mnu_timeline, self.mnu_navigate]
        enable = self.timeline != None
        for menu in menues:
            for menuitem in menu.GetMenuItems():
                menuitem.Enable(enable)
        self.mnu_file_export.Enable(enable)

    def _save_application_config(self):
        config.set_window_size(self.GetSize())
        config.set_window_maximized(self.IsMaximized())
        config.set_show_sidebar(self.mnu_view_sidebar.IsChecked())
        config.set_show_legend(self.mnu_view_legend.IsChecked())
        config.set_sidebar_width(self.main_panel.get_sidebar_width())
        config.write()

    def _save_current_timeline_data(self):
        """
        Saves settings for the timeline that is currently displayed to
        the timeline file. Date saved is:
            - currently displayed time period
        If there is no current timeline, nothing happens.
        This method should be called before a new timeline is opened
        or created or when the application is closed.
        """
        if self.timeline:
            self.timeline.set_preferred_period(self._get_time_period())

    def _export_to_image(self):
        extension_map = {"png": wx.BITMAP_TYPE_PNG}
        extensions = extension_map.keys()
        wildcard = _create_wildcard(_("Image files"), extensions)
        dialog = wx.FileDialog(self, message=_("Export to Image"),
                               wildcard=wildcard, style=wx.FD_SAVE)
        if dialog.ShowModal() == wx.ID_OK:
            path, extension = _extend_path(dialog.GetPath(), extensions, "png")
            overwrite_question = _("File '%s' exists. Overwrite?") % path
            if (not os.path.exists(path) or
                _ask_question(overwrite_question, self) == wx.YES):
                bitmap = self.main_panel.drawing_area.bgbuf
                image = wx.ImageFromBitmap(bitmap)
                image.SaveFile(path, extension_map[extension])
        dialog.Destroy()

    def _goto_date(self):
        dialog = GotoDateDialog(self, self._get_time_period().mean_time())
        if dialog.ShowModal() == wx.ID_OK:
            self._navigate_timeline(lambda tp: tp.center(dialog.time))
        dialog.Destroy()

    def _navigate_backward(self):
        self._navigate_smart_step(-1)

    def _navigate_forward(self):
        self._navigate_smart_step(1)

    def _set_initial_values_to_member_variables(self):
        """
        Instance variables usage:

        timeline            The timeline currently handled by the application
        extensions          Valid extensions for files containing timeline info
        default_extension   The default extension used in FileDialog
        wildcard            The wildcard used in FileDialog
        """
        self.timeline = None
        self.extensions = ["timeline"]
        self.default_extension = self.extensions[0]
        self.wildcard = _create_wildcard(_("Timeline files"), self.extensions)

    def _load_icon_bundle(self):
        bundle = wx.IconBundle()
        for size in ["16", "32", "48"]:
            iconpath = os.path.join(ICONS_DIR, "%s.png" % size)
            icon = wx.IconFromBitmap(wx.BitmapFromImage(wx.Image(iconpath)))
            bundle.AddIcon(icon)
        return bundle

    def _navigate_smart_step(self, direction):
    
        def months_to_year_and_month(months):
            years = int(months / 12)
            month = months - years * 12
            if month == 0:
                month = 12
                years -=1    
            return years, month
            
        tp = self._get_time_period()
        start, end = tp.start_time, tp.end_time
        year_diff = end.year - start.year
        start_months = start.year * 12 + start.month
        end_months = end.year * 12 + end.month
        month_diff = end_months - start_months
        whole_years = start.replace(year=start.year + year_diff) == end
        whole_months = start.day == 1 and end.day == 1
        direction_backward = direction < 0
        # Whole years
        if whole_years and year_diff > 0:
            if direction_backward:
                new_start = start.replace(year=start.year-year_diff)
                new_end   = start
            else:
                new_start = end
                new_end   = end.replace(year=new_start.year+year_diff)
            self._navigate_timeline(lambda tp: tp.update(new_start, new_end))
        # Whole months
        elif whole_months and month_diff > 0:
            if direction_backward:
                new_end = start
                new_start_year, new_start_month = months_to_year_and_month(
                                                        start_months - 
                                                        month_diff)
                new_start = start.replace(year=new_start_year, 
                                          month=new_start_month)
            else:
                new_start = end
                new_end_year, new_end_month = months_to_year_and_month(
                                                        end_months + 
                                                        month_diff)
                new_end = end.replace(year=new_end_year, month=new_end_month)
            self._navigate_timeline(lambda tp: tp.update(new_start, new_end))
        # No need for smart delta
        else:
            self._navigate_timeline(lambda tp: tp.move_delta(direction*tp.delta()))

    def _navigate_timeline(self, navigation_fn):
        """Shortcut for method in DrawingArea."""
        return self.main_panel.drawing_area.navigate_timeline(navigation_fn)

    def _get_time_period(self):
        """Shortcut for method in DrawingArea."""
        return self.main_panel.drawing_area.get_time_period()


class HelpBrowser(wx.Frame):

    HOME_ID = 10
    BACKWARD_ID = 20
    FORWARD_ID = 30

    def __init__(self, parent, help_system):
        wx.Frame.__init__(self, parent, title=_("Help"),
                          size=(600, 550), style=wx.DEFAULT_FRAME_STYLE)
        self.help_system = help_system
        self.history = []
        self.current_pos = -1
        self._create_gui()
        self._update_buttons()

    def show_page(self, id, type="page", change_history=True):
        """
        Where which is a tuple (type, id):

          * (page, page_id)
          * (search, search_string)
        """
        if change_history:
            if self.current_pos != -1:
                current_type, current_id = self.history[self.current_pos]
                if id == current_id:
                    return
            self.history = self.history[:self.current_pos + 1]
            self.history.append((type, id))
            self.current_pos += 1
        self._update_buttons()
        if type == "page":
            self.html_window.SetPage(self._generate_page(id))
        elif type == "search":
            self.html_window.SetPage(self.help_system.get_search_results_page(id))
        self.Show()
        self.Raise()

    def _create_gui(self):
        self.Bind(wx.EVT_CLOSE, self._window_on_close)
        self.toolbar = self.CreateToolBar()
        size = (24, 24)
        home_bmp = wx.ArtProvider.GetBitmap(wx.ART_GO_HOME, wx.ART_TOOLBAR,
                                            size)
        back_bmp = wx.ArtProvider.GetBitmap(wx.ART_GO_BACK, wx.ART_TOOLBAR,
                                            size)
        forward_bmp = wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD,
                                               wx.ART_TOOLBAR, size)
        self.toolbar.SetToolBitmapSize(size)
        # Home
        home_str = _("Go to home page")
        self.toolbar.AddLabelTool(HelpBrowser.HOME_ID, home_str,
                                  home_bmp, shortHelp=home_str)
        self.Bind(wx.EVT_TOOL, self._toolbar_on_click, id=HelpBrowser.HOME_ID)
        # Separator
        self.toolbar.AddSeparator()
        # Backward
        backward_str = _("Go back one page")
        self.toolbar.AddLabelTool(HelpBrowser.BACKWARD_ID, backward_str,
                                  back_bmp, shortHelp=backward_str)
        self.Bind(wx.EVT_TOOL, self._toolbar_on_click,
                  id=HelpBrowser.BACKWARD_ID)
        # Forward
        forward_str = _("Go forward one page")
        self.toolbar.AddLabelTool(HelpBrowser.FORWARD_ID, forward_str,
                                  forward_bmp, shortHelp=forward_str)
        self.Bind(wx.EVT_TOOL, self._toolbar_on_click,
                  id=HelpBrowser.FORWARD_ID)
        # Separator
        self.toolbar.AddSeparator()
        # Search
        self.search = wx.SearchCtrl(self.toolbar, size=(150, -1),
                                    style=wx.TE_PROCESS_ENTER)
        self.Bind(wx.EVT_TEXT_ENTER, self._search_on_text_enter, self.search)
        self.toolbar.AddControl(self.search)
        self.toolbar.Realize()
        # Html window
        self.html_window = wx.html.HtmlWindow(self)
        self.Bind(wx.html.EVT_HTML_LINK_CLICKED,
                  self._html_window_on_link_clicked, self.html_window)

    def _window_on_close(self, e):
        self.Show(False)

    def _toolbar_on_click(self, e):
        if e.GetId() == HelpBrowser.HOME_ID:
            self._go_home()
        elif e.GetId() == HelpBrowser.BACKWARD_ID:
            self._go_back()
        elif e.GetId() == HelpBrowser.FORWARD_ID:
            self._go_forward()

    def _search_on_text_enter(self, e):
        self._search(self.search.GetValue())

    def _html_window_on_link_clicked(self, e):
        url = e.GetLinkInfo().GetHref()
        if url.startswith("page:"):
            self.show_page(url[5:])
        else:
            pass
            # open in broswer

    def _go_home(self):
        self.show_page(self.help_system.home_page)

    def _go_back(self):
        if self.current_pos > 0:
            self.current_pos -= 1
            current_type, current_id = self.history[self.current_pos]
            self.show_page(current_id, type=current_type, change_history=False)

    def _go_forward(self):
        if self.current_pos < len(self.history) - 1:
            self.current_pos += 1
            current_type, current_id = self.history[self.current_pos]
            self.show_page(current_id, type=current_type, change_history=False)

    def _search(self, string):
        self.show_page(string, type="search")

    def _update_buttons(self):
        history_len = len(self.history)
        enable_backward = history_len > 1 and self.current_pos > 0
        enable_forward = history_len > 1 and self.current_pos < history_len - 1
        self.toolbar.EnableTool(HelpBrowser.BACKWARD_ID, enable_backward)
        self.toolbar.EnableTool(HelpBrowser.FORWARD_ID, enable_forward)

    def _generate_page(self, id):
        page = self.help_system.get_page(id)
        if page == None:
            error_page_html = "<h1>%s</h1><p>%s</p>" % (
                _("Page not found"),
                _("Could not find page '%s'.") % id)
            return self._wrap_in_html(error_page_html)
        else:
            return self._wrap_in_html(page.render_to_html())

    def _wrap_in_html(self, content):
        HTML_SKELETON = """
        <html>
        <head>
        </head>
        <body>
        %s
        </body>
        </html>
        """
        return HTML_SKELETON % content


class CategoriesVisibleCheckListBox(wx.CheckListBox):
    # ClientData can not be used in this control
    # (see http://docs.wxwidgets.org/stable/wx_wxchecklistbox.html)
    # This workaround will not work if items are reordered

    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent)
        self.timeline = None
        self.Bind(wx.EVT_CHECKLISTBOX, self._checklistbox_on_checklistbox, self)

    def set_timeline(self, timeline):
        if self.timeline != None:
            self.timeline.unregister(self._timeline_changed)
        self.timeline = timeline
        if self.timeline:
            self.timeline.register(self._timeline_changed)
            self._update_categories()
        else:
            self.Clear()

    def _checklistbox_on_checklistbox(self, e):
        i = e.GetSelection()
        self.categories[i].visible = self.IsChecked(i)
        self.timeline.category_edited(self.categories[i])

    def _timeline_changed(self, state_change):
        if state_change == Timeline.STATE_CHANGE_CATEGORY:
            self._update_categories()

    def _update_categories(self):
        self.categories = sort_categories(self.timeline.get_categories())
        self.Clear()
        self.AppendItems([category.name for category in self.categories])
        for i in range(0, self.Count):
            if self.categories[i].visible:
                self.Check(i)
            self.SetItemBackgroundColour(i, self.categories[i].color)


class DateTimePicker(wx.Panel):
    """
    Control to pick a Python datetime object.

    The time part will default to 00:00:00 if none is entered.
    """

    def __init__(self, parent, show_time=True):
        wx.Panel.__init__(self, parent)
        self._create_gui()
        self.show_time(show_time)

    def show_time(self, show=True):
        self.time_picker.Show(show)
        self.GetSizer().Layout()

    def get_value(self):
        """Return the selected date time as a Python datetime object."""
        date = self.date_picker.GetValue()
        date_time = dt(date.Year, date.Month+1, date.Day)
        if self.time_picker.IsShown():
            time = self.time_picker.GetValue(as_wxDateTime=True)
            date_time = date_time.replace(hour=time.Hour,
                                          minute=time.Minute)
        return date_time

    def set_value(self, value):
        if value == None:
            now = dt.now()
            value = dt(now.year, now.month, now.day)
        wx_date_time = self._python_date_to_wx_date(value)
        self.date_picker.SetValue(wx_date_time)
        self.time_picker.SetValue(wx_date_time)

    def _create_gui(self):
        self.date_picker = wx.DatePickerCtrl(self,
                               style=wx.DP_DROPDOWN|wx.DP_SHOWCENTURY)
        self.Bind(wx.EVT_DATE_CHANGED, self._date_picker_on_date_changed,
                  self.date_picker)
        self.time_picker = TimeCtrl(self, format="24HHMM")
        # Layout
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.date_picker, proportion=1,
                  flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.time_picker, proportion=0,
                  flag=wx.ALIGN_CENTER_VERTICAL)
        self.SetSizerAndFit(sizer)

    def _date_picker_on_date_changed(self, e):
        date = self.get_value()
        if date < TimePeriod.MIN_TIME:
            self.set_value(TimePeriod.MIN_TIME)
        if date > TimePeriod.MAX_TIME:
            self.set_value(TimePeriod.MAX_TIME)

    def _python_date_to_wx_date(self, py_date):
        return wx.DateTimeFromDMY(py_date.day, py_date.month-1, py_date.year,
                                  py_date.hour, py_date.minute,
                                  py_date.second)


class MainPanel(wx.Panel):
    """
    Panel that covers the whole client area of MainFrame.

    Contains a sidebar that can be hidden and shown and DrawingArea.
    """

    def __init__(self, parent):
        """Create the Main Panel."""
        wx.Panel.__init__(self, parent)
        self.sidebar_width = config.get_sidebar_width()
        self._create_gui()
        self.show_sidebar()
        if not config.get_show_sidebar():
            self.hide_sidebar()

    def get_sidebar_width(self):
        return self.sidebar_width

    def show_sidebar(self):
        self.splitter.SplitVertically(self.sidebar, self.drawing_area,
                                      self.sidebar_width)

    def hide_sidebar(self):
        self.splitter.Unsplit(self.sidebar)

    def _create_gui(self):
        """Create the controls of the Main Panel."""
        self.splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)
        self.splitter.SetMinimumPaneSize(50)
        self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED,
                  self._splitter_on_splitter_sash_pos_changed, self.splitter)
        # DrawingArea
        self.drawing_area = DrawingArea(self.splitter)
        # Sidebar
        self.sidebar = wx.Panel(self.splitter, style=wx.BORDER_NONE)
        self.catbox = CategoriesVisibleCheckListBox(self.sidebar)
        # Container sizer
        pane_sizer = wx.BoxSizer(wx.VERTICAL)
        pane_sizer.Add(self.catbox, flag=wx.GROW, proportion=1)
        self.sidebar.SetSizer(pane_sizer)
        # Splitter in sizer
        globalSizer = wx.BoxSizer(wx.HORIZONTAL)
        globalSizer.Add(self.splitter, flag=wx.GROW, proportion=1)
        self.SetSizer(globalSizer)

    def _splitter_on_splitter_sash_pos_changed(self, e):
        self.sidebar_width = self.splitter.GetSashPosition()


class DrawingArea(wx.Panel):
    """
    Window on which the timeline is drawn.

    This class has information about what timeline and what part of the
    timeline to draw and makes sure that the timeline is redrawn whenever it is
    needed.

    Double buffering is used to avoid flicker while drawing. This is
    accomplished by always drawing to a background buffer: bgbuf. The paint
    method of the control thus only draws the background buffer to the screen.

    Scrolling and zooming of the timeline is implemented in this class. This is
    done whenever the mouse wheel is scrolled (_window_on_mousewheel).
    Moving also takes place when the mouse is dragged while pressing the left
    mouse key (_window_on_motion).

    Selection of a period on the timeline (period = any number of minor strips)
    is also implemented in this class. A selection is done in the following
    way: Press and hold down the Control key on the keyboard, move the mouse to
    the first minor strip to be selected and then press and hold down the left
    mouse key. Now, while moving the mouse over the timeline, the minor strips
    will be selected.

    What happens is that when the left mouse button is pressed
    (_window_on_left_down) the variable self._current_time is set to the
    time on the timeline where the mouse is. This is the anchor point for the
    selection. When the mouse is moved (_window_on_motion) and left mouse button
    is pressed and the Control key is held down the method
    self._mark_selected_minor_strips(evt.m_x) is called. This method marks all
    minor strips between the anchor point and the current point (evt.m_x).
    When the mouse button is released the selection ends.
    """

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, style=wx.NO_BORDER)
        self._create_gui()
        self._set_initial_values_to_member_variables()
        self._set_colors_and_styles()
        self.timeline = None
        logging.debug("Init done in DrawingArea")

    def set_timeline(self, timeline):
        """Inform what timeline to draw."""
        if self.timeline != None:
            self.timeline.unregister(self._timeline_changed)
        self.timeline = timeline
        if self.timeline:
            self.timeline.register(self._timeline_changed)
            self.time_period = timeline.get_preferred_period()
            self._redraw_timeline()
            self.Enable()
            self.SetFocus()
        else:
            self.Disable()

    def show_hide_legend(self, show):
        self.show_legend = show
        if self.timeline:
            self._redraw_timeline()

    def get_time_period(self):
        """Return currently displayed time period."""
        if self.timeline == None:
            raise Exception(_("No timeline set"))
        return self.time_period

    def navigate_timeline(self, navigation_fn):
        """
        Perform a navigation operation followed by a redraw.

        The navigation_fn should take one argument which is the time period
        that should be manipulated in order to carry out the navigation
        operation.

        Should the navigation operation fail (max zoom level reached, etc) a
        message will be displayed in the statusbar.

        Note: The time period should never be modified directly. This method
        should always be used instead.
        """
        if self.timeline == None:
            raise Exception(_("No timeline set"))
        try:
            navigation_fn(self.time_period)
            self._redraw_timeline()
            wx.GetTopLevelParent(self).SetStatusText("")
        except (ValueError, OverflowError), e:
            wx.GetTopLevelParent(self).SetStatusText(e.message)

    def _create_gui(self):
        self.Bind(wx.EVT_SIZE, self._window_on_size)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self._window_on_erase_background)
        self.Bind(wx.EVT_PAINT, self._window_on_paint)
        self.Bind(wx.EVT_LEFT_DOWN, self._window_on_left_down)
        self.Bind(wx.EVT_LEFT_DCLICK, self._window_on_left_dclick)
        self.Bind(wx.EVT_LEFT_UP, self._window_on_left_up)
        self.Bind(wx.EVT_MOTION, self._window_on_motion)
        self.Bind(wx.EVT_MOUSEWHEEL, self._window_on_mousewheel)
        self.Bind(wx.EVT_KEY_DOWN, self._window_on_key_down)
        self.Bind(wx.EVT_KEY_UP, self._window_on_key_up)

    def _window_on_size(self, event):
        """
        Event handler used when the window has been resized.

        Called at the application start and when the frame is resized.

        Here we create a new background buffer with the new size and draw the
        timeline onto it.
        """
        logging.debug("Resize event in DrawingArea: %s", self.GetSizeTuple())
        width, height = self.GetSizeTuple()
        self.bgbuf = wx.EmptyBitmap(width, height)
        self._redraw_timeline()

    def _window_on_erase_background(self, event):
        # For double buffering
        pass

    def _window_on_paint(self, event):
        """
        Event handler used when the window needs repainting.

        Called at the application start, after resizing, or when the window
        becomes active.

        Here we just draw the background buffer onto the screen.

        Defining a dc is crucial. Even if it is not used.
        """
        logging.debug("Paint event in DrawingArea")
        dc = wx.AutoBufferedPaintDC(self)
        dc.BeginDrawing()
        dc.DrawBitmap(self.bgbuf, 0, 0, True)
        dc.EndDrawing()

    def _window_on_left_down(self, evt):
        """
        Event handler used when the left mouse button has been pressed.

        This event establishes a new current time on the timeline.

        If the mouse hits an event that event will be selected.
        """
        logging.debug("Left mouse pressed event in DrawingArea")
        self._set_new_current_time(evt.m_x)
        posAtEvent = self._toggle_event_selection(evt.m_x, evt.m_y,
                                                  evt.m_controlDown)
        if not posAtEvent:
            if evt.m_controlDown:
                self._set_select_period_cursor()
            else:
                self._set_drag_cursor()
        evt.Skip()

    def _window_on_left_dclick(self, evt):
        """
        Event handler used when the left mouse button has been double clicked.

        If the mouse hits an event, a dialog opens for editing this event.
        Otherwise a dialog for creating a new event is opened.
        """
        logging.debug("Left Mouse doubleclicked event in DrawingArea")
        event = self.drawing_algorithm.event_at(evt.m_x, evt.m_y)
        if event:
            _edit_event(self.timeline, event)
        else:
            _create_new_event(self.timeline, self._current_time,
                              self._current_time)

    def _window_on_left_up(self, evt):
        """
        Event handler used when the left mouse button has been released.

        If there is an ongoing selection-marking, the dialog for creating an
        event will be opened, and the selection-marking will be ended.
        """
        logging.debug("Left mouse released event in DrawingArea")
        if self.is_selecting:
            self._end_selection_and_create_event(evt.m_x)
        self.is_selecting = False
        self.is_scrolling = False
        self._set_default_cursor()

    def _window_on_motion(self, evt):
        """
        Event handler used when the mouse has been moved.

        If the mouse is over an event, the name of that event will be printed
        in the status bar.

        If the left mouse key is down one of two things happens depending on if
        the Control key is down or not. If it is down a selection-marking takes
        place and the minor strips passed by the mouse will be selected.  If
        the Control key is up the timeline will scroll.
        """
        logging.debug("Mouse move event in DrawingArea")
        if evt.Dragging:
            self._display_eventname_in_statusbar(evt.m_x, evt.m_y)
        if evt.m_leftDown:
            if self.is_scrolling:
                self._scroll(evt.m_x)
            elif self.is_selecting:
                self._mark_selected_minor_strips(evt.m_x)
            else:
                if evt.m_controlDown:
                    self._mark_selected_minor_strips(evt.m_x)
                    self.is_selecting = True
                else:
                    self._scroll(evt.m_x)
                    self.is_scrolling = True

    def _window_on_mousewheel(self, evt):
        """
        Event handler used when the mouse wheel is rotated.

        If the Control key is pressed at the same time as the mouse wheel is
        scrolled the timeline will be zoomed, otherwise it will be scrolled.
        """
        logging.debug("Mouse wheel event in DrawingArea")
        direction = _step_function(evt.m_wheelRotation)
        if evt.ControlDown():
            self._zoom_timeline(direction)
        else:
            delta = data.mult_timedelta(self.time_period.delta(),
                                        direction / 10.0)
            self._scroll_timeline(delta)

    def _window_on_key_down(self, evt):
        """
        Event handler used when a keyboard key has been pressed.

        The following keys are handled:
        Key         Action
        --------    ------------------------------------
        Delete      Delete any selected event(s)
        Control     Change cursor
        """
        logging.debug("Key down event in DrawingArea")
        keycode = evt.GetKeyCode()
        if keycode == wx.WXK_DELETE:
            self._delete_selected_events()
        evt.Skip()

    def _window_on_key_up(self, evt):
        keycode = evt.GetKeyCode()
        if keycode == wx.WXK_CONTROL:
            self._set_default_cursor()

    def _timeline_changed(self, state_change):
        if state_change == Timeline.STATE_CHANGE_ANY:
            self._redraw_timeline()

    def _set_initial_values_to_member_variables(self):
        """
        Instance variables usage:

        _current_time       This variable is set to the time on the timeline
                            where the mouse button is clicked when the left
                            mouse button is used
        _mark_selection     Processing flag indicating ongoing selection of a
                            time period
        timeline            The timeline currently handled by the application
        time_period         The part of the timeline currently displayed in the
                            drawing area
        drawing_algorithm   The algorithm used to draw the timeline
        bgbuf               The bitmap to which the drawing methods draw the
                            timeline. When the EVT_PAINT occurs this bitmap
                            is painted on the screen. This is a buffer drawing
                            approach for avoiding screen flicker.
        is_scrolling        True when scrolling with the mouse takes place.
                            It is set True in mouse_has_moved and set False
                            in left_mouse_button_released.
        is_selecting        True when selecting with the mouse takes place
                            It is set True in mouse_has_moved and set False
                            in left_mouse_button_released.
        """
        self._current_time = None
        self._mark_selection = False
        self.bgbuf = None
        self.timeline = None
        self.time_period = None
        self.drawing_algorithm = drawing.get_algorithm()
        self.is_scrolling = False
        self.is_selecting = False
        self.show_legend = config.get_show_legend()

    def _set_colors_and_styles(self):
        """Define the look and feel of the drawing area."""
        self.SetBackgroundColour(wx.WHITE)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self._set_default_cursor()
        self.Disable()

    def _redraw_timeline(self, period_selection=None):
        """Draw the timeline onto the background buffer."""
        logging.debug("Draw timeline to bgbuf")
        memdc = wx.MemoryDC()
        memdc.SelectObject(self.bgbuf)
        try:
            memdc.BeginDrawing()
            memdc.SetBackground(wx.Brush(wx.WHITE, wx.SOLID))
            memdc.Clear()
            if self.timeline:
                current_events = self.timeline.get_events(self.time_period)
                self.drawing_algorithm.draw(memdc, self.time_period,
                                            current_events,
                                            period_selection,
                                            self.show_legend)
            memdc.EndDrawing()
            del memdc
            self.Refresh()
            self.Update()
        except Exception, ex:
            self.bgbuf = None
            logging.fatal("Error in drawing", exc_info=ex)

    def _scroll(self, xpixelpos):
        if self._current_time:
            delta = (self.drawing_algorithm.metrics.get_time(xpixelpos) -
                        self._current_time)
            self._scroll_timeline(delta)

    def _set_new_current_time(self, current_x):
        self._current_time = self.drawing_algorithm.metrics.get_time(current_x)
        logging.debug("Marked time " + self._current_time.isoformat("-"))

    def _toggle_event_selection(self, xpixelpos, ypixelpos, control_down):
        """
        If the given position is within the boundaries of an event that event
        will be selected or unselected depending on the current selection
        state of the event. If the Control key is down all other events
        selection state are preserved. This means that previously selected
        events will stay selected. If the Control keys is not down all other
        events will be unselected.

        If the given position isn't within an event all selected events will
        be unselected.

        Return True if the given position was with an event, otherwise
        return False.
        """
        event = self.drawing_algorithm.event_at(xpixelpos, ypixelpos)
        if event:
            selected = event.selected
            if not control_down:
                self.timeline.reset_selected_events()
            self.timeline.select_event(event, not selected)
        else:
            self.timeline.reset_selected_events()
        return event != None

    def _end_selection_and_create_event(self, current_x):
        self._mark_selection = False
        period_selection = self._get_period_selection(current_x)
        start, end = period_selection
        _create_new_event(self.timeline, start, end)
        self._redraw_timeline()

    def _display_eventname_in_statusbar(self, xpixelpos, ypixelpos):
        """
        If the given position is within the boundaries of an event, the name of
        that event will be displayed in the status bar, otherwise the status
        bar text will be removed.
        """
        event = self.drawing_algorithm.event_at(xpixelpos, ypixelpos)
        if event != None:
            self._display_text_in_statusbar(event.text)
        else:
            self._reset_text_in_statusbar()

    def _mark_selected_minor_strips(self, current_x):
        """Selection-marking starts or continues."""
        self._mark_selection = True
        period_selection = self._get_period_selection(current_x)
        self._redraw_timeline(period_selection)

    def _scroll_timeline(self, delta):
        self.navigate_timeline(lambda tp: tp.move_delta(-delta))

    def _zoom_timeline(self, direction=0):
        self.navigate_timeline(lambda tp: tp.zoom(direction))

    def _delete_selected_events(self):
        """After acknowledge from the user, delete all selected events."""
        if _ask_question(_("Are you sure to delete?"), self) == wx.YES:
            self.timeline.delete_selected_events()

    def _get_period_selection(self, current_x):
        """Return a tuple containing the start and end time of a selection."""
        start = self._current_time
        end   = self.drawing_algorithm.metrics.get_time(current_x)
        if start > end:
            start, end = end, start
        period_selection = self.drawing_algorithm.snap_selection((start,end))
        return period_selection

    def _display_text_in_statusbar(self, text):
        wx.GetTopLevelParent(self).SetStatusText(text)

    def _reset_text_in_statusbar(self):
        wx.GetTopLevelParent(self).SetStatusText("")

    def _set_select_period_cursor(self):
        self.SetCursor(wx.StockCursor(wx.CURSOR_IBEAM))

    def _set_drag_cursor(self):
        self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))

    def _set_default_cursor(self):
        """
        Set the cursor to it's default shape when it is in the timeline
        drawing area.
        """
        self.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))


class EventEditor(wx.Dialog):
    """Dialog used for creating and editing events."""

    def __init__(self, parent, id, title, timeline, start=None, end=None,
                 event=None):
        """
        Create a event editor dialog.

        The 'event' argument is optional. If it is given the dialog is used
        to edit this event and the controls are filled with data from
        the event and the arguments 'start' and 'end' are ignored.

        If the 'event' argument isn't given the dialog is used to create a
        new event, and the controls for start and end time are initially
        filled with data from the arguments 'start' and 'end' if they are
        given. Otherwise they will default to today.
        """
        wx.Dialog.__init__(self, parent, id, title,
                           style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        self.timeline = timeline
        self.event = event
        self._create_gui()
        self._fill_controls_with_data(start, end)
        self._set_initial_focus()

    def _create_gui(self):
        """Create the controls of the dialog."""
        # Groupbox
        groupbox = wx.StaticBox(self, wx.ID_ANY, _("Event Properties"))
        groupbox_sizer = wx.StaticBoxSizer(groupbox, wx.VERTICAL)
        # Grid
        grid = wx.FlexGridSizer(4, 2, BORDER, BORDER)
        grid.AddGrowableCol(1)
        # Grid: When: Label + DateTimePickers
        grid.Add(wx.StaticText(self, label=_("When:")),
                 flag=wx.ALIGN_CENTER_VERTICAL)
        self.dtp_start = DateTimePicker(self)
        self.lbl_to = wx.StaticText(self, label=_("to"))
        self.dtp_end = DateTimePicker(self)
        when_box = wx.BoxSizer(wx.HORIZONTAL)
        when_box.Add(self.dtp_start, proportion=1)
        when_box.AddSpacer(BORDER)
        when_box.Add(self.lbl_to, flag=wx.ALIGN_CENTER_VERTICAL|wx.RESERVE_SPACE_EVEN_IF_HIDDEN)
        when_box.AddSpacer(BORDER)
        when_box.Add(self.dtp_end, proportion=1,
                     flag=wx.RESERVE_SPACE_EVEN_IF_HIDDEN)
        grid.Add(when_box)
        # Grid: When: Checkboxes
        grid.AddStretchSpacer()
        when_box_props = wx.BoxSizer(wx.HORIZONTAL)
        self.chb_period = wx.CheckBox(self, label=_("Period"))
        self.Bind(wx.EVT_CHECKBOX, self._chb_period_on_checkbox,
                  self.chb_period)
        when_box_props.Add(self.chb_period)
        self.chb_show_time = wx.CheckBox(self, label=_("Show time"))
        self.Bind(wx.EVT_CHECKBOX, self._chb_show_time_on_checkbox,
                  self.chb_show_time)
        when_box_props.Add(self.chb_show_time)
        grid.Add(when_box_props)
        # Grid: Text
        self.txt_text = wx.TextCtrl(self, wx.ID_ANY)
        grid.Add(wx.StaticText(self, label=_("Text:")),
                 flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.txt_text, flag=wx.EXPAND)
        # Grid: Category
        self.lst_category = wx.Choice(self, wx.ID_ANY)
        grid.Add(wx.StaticText(self, label=_("Category:")),
                 flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.lst_category)
        groupbox_sizer.Add(grid, flag=wx.ALL|wx.EXPAND, border=BORDER)
        # Plugins
        self.event_data_plugins = []
        notebook = wx.Notebook(self, style=wx.BK_DEFAULT)
        for plugin in data.get_event_data_plugins():
            panel = wx.Panel(notebook)
            notebook.AddPage(panel, plugin.get_name())
            editor = plugin.create_editor(panel)
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(editor, flag=wx.EXPAND, proportion=1)
            panel.SetSizer(sizer)
            self.event_data_plugins.append((plugin, editor))
        groupbox_sizer.Add(notebook, border=BORDER, flag=wx.ALL|wx.EXPAND,
                           proportion=1)
        # Main (vertical layout)
        main_box = wx.BoxSizer(wx.VERTICAL)
        # Main: Groupbox
        main_box.Add(groupbox_sizer, flag=wx.EXPAND|wx.ALL, border=BORDER,
                     proportion=1)
        # Main: Checkbox
        self.chb_add_more = wx.CheckBox(self, label=_("Add more events after this one"))
        main_box.Add(self.chb_add_more, flag=wx.ALL, border=BORDER)
        # Main: Buttons
        button_box = self.CreateStdDialogButtonSizer(wx.OK|wx.CANCEL)
        self.Bind(wx.EVT_BUTTON, self._btn_ok_on_click, id=wx.ID_OK)
        main_box.Add(button_box, flag=wx.EXPAND|wx.ALL, border=BORDER)
        # Hide if not creating new
        if self.event != None:
            self.chb_add_more.Show(False)
        # Realize
        self.SetSizerAndFit(main_box)

    def _btn_ok_on_click(self, evt):
        """
        Add new or update existing event.

        If the Close-on-ok checkbox is checked the dialog is also closed.
        """
        logging.debug("_btn_ok_on_click")
        try:
            # Input value retrieval and validation
            start_time = self.dtp_start.get_value()
            end_time = start_time
            if self.chb_period.IsChecked():
                end_time = self.dtp_end.get_value()
            selection = self.lst_category.GetSelection()
            category = self.lst_category.GetClientData(selection)
            if start_time > end_time:
                raise TxtException(_("End must be > Start"), self.dtp_start)
            name = _parse_text_from_textbox(self.txt_text, _("Text"))
            # Update existing event
            if self.updatemode:
                self.event.update(start_time, end_time, name, category)
                for plugin, editor in self.event_data_plugins:
                    self.event.set_data(plugin.get_id(),
                                        plugin.get_editor_data(editor))
                self.timeline.event_edited(self.event)
            # Create new event
            else:
                self.event = Event(start_time, end_time, name, category)
                for plugin, editor in self.event_data_plugins:
                    self.event.set_data(plugin.get_id(),
                                        plugin.get_editor_data(editor))
                self.timeline.add_event(self.event)
            # Close the dialog ?
            if self.chb_add_more.GetValue():
                self.txt_text.SetValue("")
                for plugin, editor in self.event_data_plugins:
                    plugin.clear_editor_data(editor)
            else:
                self._close()
        except TxtException, ex:
            _display_error_message("%s" % ex.error_message)
            _set_focus_and_select(ex.control)

    def _chb_period_on_checkbox(self, e):
        self._show_to_time(e.IsChecked())

    def _chb_show_time_on_checkbox(self, e):
        self.dtp_start.show_time(e.IsChecked())
        self.dtp_end.show_time(e.IsChecked())

    def _show_to_time(self, show=True):
        self.lbl_to.Show(show)
        self.dtp_end.Show(show)

    def _fill_controls_with_data(self, start=None, end=None):
        """Initially fill the controls in the dialog with data."""
        if self.event == None:
            self.chb_period.SetValue(False)
            self.chb_show_time.SetValue(False)
            text = ""
            category = None
            self.updatemode = False
        else:
            start = self.event.time_period.start_time
            end = self.event.time_period.end_time
            text = self.event.text
            category = self.event.category
            for plugin, editor in self.event_data_plugins:
                data = self.event.get_data(plugin.get_id())
                if data != None:
                    plugin.set_editor_data(editor, data)
            self.updatemode = True
        if start != None and end != None:
            show_time = (start.time() != time(0, 0, 0) or
                         end.time() != time(0, 0, 0))
            self.chb_show_time.SetValue(show_time)
            self.chb_period.SetValue(start != end)
        self.dtp_start.set_value(start)
        self.dtp_end.set_value(end)
        self.txt_text.SetValue(text)
        # Category Choice
        self.lst_category.Append("", None) # The None-category
        selection_set = False
        current_item_index = 1
        for cat in sort_categories(self.timeline.get_categories()):
            self.lst_category.Append(cat.name, cat)
            if cat == category:
                self.lst_category.SetSelection(current_item_index)
                selection_set = True
            current_item_index += 1
        if not selection_set:
            self.lst_category.SetSelection(0)
        self.chb_add_more.SetValue(False)
        self._show_to_time(self.chb_period.IsChecked())
        self.dtp_start.show_time(self.chb_show_time.IsChecked())
        self.dtp_end.show_time(self.chb_show_time.IsChecked())

    def _set_initial_focus(self):
        self.dtp_start.SetFocus()

    def _close(self):
        """
        Close the dialog.

        Make sure that no events are selected after the dialog is closed.
        """
        self.timeline.reset_selected_events()
        self.EndModal(wx.ID_OK)


class CategoriesEditor(wx.Dialog):
    """
    Dialog used to edit categories of a timeline.

    The edits happen immediately. In other words: when the dialog is closing
    all edits have been applied already.
    """

    def __init__(self, parent, timeline):
        wx.Dialog.__init__(self, parent, title=_("Edit Categories"))
        self._create_gui()
        self.timeline = timeline
        # Note: We must unregister before we close this dialog. When we close
        # this dialog it will be disposed and self._timeline_changed will no
        # longer exist. The next time the timeline gets updated it will try to
        # call a method that does not exist.
        self.timeline.register(self._timeline_changed)
        self._update_categories()

    def _create_gui(self):
        self.Bind(wx.EVT_CLOSE, self._window_on_close)
        # The list box
        self.lst_categories = wx.ListBox(self, size=(200, 180),
                                         style=wx.LB_SINGLE)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self._lst_categories_on_dclick,
                  self.lst_categories)
        # The Add button
        btn_add = wx.Button(self, wx.ID_ADD)
        self.Bind(wx.EVT_BUTTON, self._btn_add_on_click, btn_add)
        # The Delete button
        btn_del = wx.Button(self, wx.ID_DELETE)
        self.Bind(wx.EVT_BUTTON, self._btn_del_on_click, btn_del)
        # The close button
        btn_close = wx.Button(self, wx.ID_CLOSE)
        btn_close.SetDefault()
        btn_close.SetFocus()
        self.SetAffirmativeId(wx.ID_CLOSE)
        self.Bind(wx.EVT_BUTTON, self._btn_close_on_click, btn_close)
        self.lst_categories.Bind(wx.EVT_KEY_DOWN, self._lst_categories_on_key_down)
        # Setup layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.lst_categories, flag=wx.ALL|wx.EXPAND, border=BORDER)
        button_box = wx.BoxSizer(wx.HORIZONTAL)
        button_box.Add(btn_add, flag=wx.RIGHT, border=BORDER)
        button_box.Add(btn_del, flag=wx.RIGHT, border=BORDER)
        button_box.AddStretchSpacer()
        button_box.Add(btn_close, flag=wx.LEFT, border=BORDER)
        vbox.Add(button_box, flag=wx.ALL|wx.EXPAND, border=BORDER)
        self.SetSizerAndFit(vbox)
        self.lst_categories.SetFocus()

    def _window_on_close(self, e):
        # This will always be called before the dialog closes so we can do the
        # unregister here.
        self.timeline.unregister(self._timeline_changed)
        self.EndModal(wx.ID_CLOSE)

    def _lst_categories_on_dclick(self, e):
        selection = e.GetSelection()
        dialog = CategoryEditor(self, _("Edit Category"), self.timeline,
                                e.GetClientData())
        if dialog.ShowModal() == wx.ID_OK:
            self.timeline.category_edited(dialog.get_edited_category())
        dialog.Destroy()

    def _btn_add_on_click(self, e):
        dialog = CategoryEditor(self, _("Add Category"), self.timeline, None)
        if dialog.ShowModal() == wx.ID_OK:
            self.timeline.add_category(dialog.get_edited_category())
        dialog.Destroy()

    def _btn_del_on_click(self, e):
        self._delete_selected_category()

    def _btn_close_on_click(self, e):
        self.Close()

    def _lst_categories_on_key_down(self, e):
        logging.debug("Key down event in CategoriesEditor")
        keycode = e.GetKeyCode()
        if keycode == wx.WXK_DELETE:
            self._delete_selected_category()
        e.Skip()

    def _timeline_changed(self, state_change):
        if state_change == Timeline.STATE_CHANGE_CATEGORY:
            self._update_categories()

    def _delete_selected_category(self):
        selection = self.lst_categories.GetSelection()
        if selection != wx.NOT_FOUND:
            if _ask_question(_("Are you sure to delete?"), self) == wx.YES:
                cat = self.lst_categories.GetClientData(selection)
                self.timeline.delete_category(cat)

    def _update_categories(self):
        self.lst_categories.Clear()
        for category in sort_categories(self.timeline.get_categories()):
            self.lst_categories.Append(category.name, category)


class CategoryEditor(wx.Dialog):
    """
    Dialog used to edit a category.

    The edited category can be fetched with get_edited_category.
    """

    def __init__(self, parent, title, timeline, category):
        wx.Dialog.__init__(self, parent, title=title)
        self._create_gui()
        self.timeline = timeline
        self.category = category
        if self.category == None:
            self.category = Category("", (200, 200, 200), True)
        self.txt_name.SetValue(self.category.name)
        self.colorpicker.SetColour(self.category.color)
        self.chb_visible.SetValue(self.category.visible)

    def get_edited_category(self):
        return self.category

    def _create_gui(self):
        # The name text box
        self.txt_name = wx.TextCtrl(self, size=(150, -1))
        # The color chooser
        self.colorpicker = colourselect.ColourSelect(self)
        # The visible check box
        self.chb_visible = wx.CheckBox(self)
        # Setup layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        # Grid for controls
        field_grid = wx.FlexGridSizer(3, 2, BORDER, BORDER)
        field_grid.Add(wx.StaticText(self, label=_("Name:")),
                       flag=wx.ALIGN_CENTER_VERTICAL)
        field_grid.Add(self.txt_name)
        field_grid.Add(wx.StaticText(self, label=_("Color:")),
                       flag=wx.ALIGN_CENTER_VERTICAL)
        field_grid.Add(self.colorpicker)
        field_grid.Add(wx.StaticText(self, label=_("Visible:")),
                       flag=wx.ALIGN_CENTER_VERTICAL)
        field_grid.Add(self.chb_visible)
        vbox.Add(field_grid, flag=wx.EXPAND|wx.ALL, border=BORDER)
        # Buttons
        button_box = self.CreateStdDialogButtonSizer(wx.OK|wx.CANCEL)
        self.Bind(wx.EVT_BUTTON, self._btn_ok_on_click, id=wx.ID_OK)
        vbox.Add(button_box, flag=wx.ALL|wx.EXPAND, border=BORDER)
        self.SetSizerAndFit(vbox)
        _set_focus_and_select(self.txt_name)

    def _btn_ok_on_click(self, e):
        name = self.txt_name.GetValue().strip()
        if not self._name_valid(name):
            _display_error_message(_("Category name '%s' not valid. Must be non-empty.") % name,
                                   self)
            return
        if self._name_in_use(name):
            _display_error_message(_("Category name '%s' already in use.") % name,
                                   self)
            return
        self.category.name = name
        self.category.color = self.colorpicker.GetColour()
        self.category.visible = self.chb_visible.IsChecked()
        self.EndModal(wx.ID_OK)

    def _name_valid(self, name):
        return len(name) > 0

    def _name_in_use(self, name):
        for cat in self.timeline.get_categories():
            if cat != self.category and cat.name == name:
                return True
        return False


class GotoDateDialog(wx.Dialog):

    def __init__(self, parent, time):
        wx.Dialog.__init__(self, parent, title=_("Go to Date"))
        self._create_gui()
        self.dtpc.set_value(time)

    def _create_gui(self):
        self.dtpc = DateTimePicker(self)
        checkbox = wx.CheckBox(self, label=_("Show time"))
        checkbox.SetValue(False)
        self.dtpc.show_time(checkbox.IsChecked())
        self.Bind(wx.EVT_CHECKBOX, self._chb_show_time_on_checkbox, checkbox)
        # Layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(checkbox, flag=wx.LEFT|wx.TOP|wx.RIGHT,
                 border=BORDER, proportion=1)
        vbox.Add(self.dtpc, flag=wx.EXPAND|wx.RIGHT|wx.BOTTOM|wx.LEFT,
                 border=BORDER, proportion=1)
        self.Bind(wx.EVT_BUTTON, self._btn_ok_on_click, id=wx.ID_OK)
        button_box = self.CreateStdDialogButtonSizer(wx.OK|wx.CANCEL)
        vbox.Add(button_box, flag=wx.ALL|wx.EXPAND, border=BORDER)
        self.SetSizerAndFit(vbox)

    def _chb_show_time_on_checkbox(self, e):
        self.dtpc.show_time(e.IsChecked())

    def _btn_ok_on_click(self, e):
        self.time = self.dtpc.get_value()
        self.EndModal(wx.ID_OK)


class TxtException(ValueError):
    """
    Thrown if a text control contains an invalid value.

    The constructor takes two arguments.

    The first is a text string containing any exception text.
    The seocond is a TextCtrl object.
    """
    def __init__(self, error_message, control):
        ValueError.__init__(self, error_message)
        self.error_message = error_message
        self.control = control


def sort_categories(categories):
    sorted_categories = list(categories)
    sorted_categories.sort(cmp, lambda x: x.name.lower())
    return sorted_categories


def _create_new_event(timeline, start=None, end=None):
    """Open a dialog for creating a new event."""
    dlg = EventEditor(None, -1, _("Create Event"), timeline, start, end)
    dlg.ShowModal()
    dlg.Destroy()


def _edit_event(timeline, event):
    """Open a dialog for updating properties of a marked event"""
    dlg = EventEditor(None, -1, _("Edit Event"), timeline, event=event)
    dlg.ShowModal()
    dlg.Destroy()


def _edit_categories(timeline):
    dialog = CategoriesEditor(None, timeline)
    dialog.ShowModal()
    dialog.Destroy()


def _set_focus_and_select(ctrl):
    ctrl.SetFocus()
    if hasattr(ctrl, "SelectAll"):
        ctrl.SelectAll()


def _parse_text_from_textbox(txt, name):
    """
    Return a text control field.

    If the value is an empty string the method raises a ValueError
    exception and sets focus on the control.

    If the value is valid the text in the control is returned
    """
    data = txt.GetValue().strip()
    if len(data) == 0:
        raise TxtException, (_("Field '%s' can't be empty.") % name, txt)
    return data


def _display_error_message(message, parent=None):
    """Display an error message in a modal dialog box"""
    dial = wx.MessageDialog(parent, message, _("Error"), wx.OK | wx.ICON_ERROR)
    dial.ShowModal()


def _ask_question(question, parent=None):
    """Ask a yes/no question and return the reply."""
    return wx.MessageBox(question, _("Question"),
                         wx.YES_NO|wx.CENTRE|wx.NO_DEFAULT, parent)


def _step_function(x_value):
    """
    A step function.

            {-1   when x < 0
    F(x) =  { 0   when x = 0
            { 1   when x > 0
    """
    y_value = 0
    if x_value < 0:
        y_value = -1
    elif x_value > 0:
        y_value = 1
    return y_value


def _create_wildcard(text, extensions):
    """
    Create wildcard for use in open/save dialogs.
    """
    return "%s (%s)|%s" % (text,
                           ", ".join(["*." + e for e in extensions]),
                           ";".join(["*." + e for e in extensions]))


def _extend_path(path, valid_extensions, default_extension):
    """Return tuple (path, extension) ensuring that path has extension."""
    for extension in valid_extensions:
        if path.endswith("." + extension):
            return (path, extension)
    return (path + "." + default_extension, default_extension)


def _create_button_box(parent, ok_method, cancel_method=None):
    """
    Convenience method for creating a button box control.

    The control contains one OK button and one Cancel or Close button.
    """
    button_box = wx.StdDialogButtonSizer()
    btn_ok = wx.Button(parent, wx.ID_OK)
    btn_cancel = wx.Button(parent, wx.ID_CANCEL)
    btn_ok.SetDefault()
    button_box.SetCancelButton(btn_cancel)
    button_box.SetAffirmativeButton(btn_ok)
    button_box.Realize()
    parent.Bind(wx.EVT_BUTTON, ok_method, btn_ok)
    if cancel_method != None:
        parent.Bind(wx.EVT_BUTTON, cancel_method, id=wx.ID_CANCEL)
        parent.Bind(wx.EVT_BUTTON, cancel_method, btn_cancel)
    parent.SetEscapeId(btn_cancel.GetId())
    parent.SetDefaultItem(btn_ok)
    parent.SetAffirmativeId(btn_ok.GetId())
    return button_box

