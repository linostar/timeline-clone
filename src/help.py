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
A wiki-like help system with a GUI browser.

Help pages are defined in separate modules like this:

  from help import install_page
  install_page(...)
  install_page(...)

Usage:

  import help
  help.init(wx_main_window, "home_page", "/path/to/help/resources",
            ["help_pages_module1"])
  help.show_page("help")
"""


import re
from docutils.core import publish_parts

import wx
import wx.html


pages = {}
home_page = ""
media_path = ""
gui_browser = None


class HelpBrowser(wx.Frame):

    HOME_ID = 10
    BACKWARD_ID = 20
    FORWARD_ID = 30

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, title=_("Help"),
                          size=(550, 550), style=wx.DEFAULT_FRAME_STYLE)
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
            self.html_window.SetPage(self._generate_search_result_page(id))

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
        self.show_page(home_page)

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

    def _generate_search_result_page(self, search_string):
        matches = get_pages_matching_search(search_string)
        # search
        tex = ""
        tex += "<ul>"
        for page in matches:
            tex += "<li>"
            tex += "<a href=\"page:%s\">%s</a>" % (page.id, page.header)
            tex += "</li>"
        tex += "</ul>"
        search_page_html = "<h1>%s</h1>%s" % (
            _("Search results for '%s'") % search_string,
            tex)
        return self._wrap_in_html(search_page_html)

    def _generate_page(self, id):
        page = get_page(id)
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


class HelpPage(object):

    def __init__(self, id, header, body, related_pages):
        self.id = id
        self.header = header
        self.body = body
        self.related_pages = related_pages

    def render_to_html(self, header_level=1):
        html = u"<h1>%s</h1>%s" % (self.header, _rst_to_html(self.body))
        # Change headers
        # Our link markup: Replace Help(foo) with proper link
        while True:
            match = re.search(r"Help\(([^)]+)\)", html)
            if match:
                page = get_page(match.group(1))
                replacement = "??"
                if page:
                    replacement = "<a href=\"page:%s\">%s</a>" % (
                        match.group(1), page.header)
                html = html[0:match.start(0)] + replacement + \
                       html[match.end(0):]
            else:
                break
        # Our link markup: Replace HelpFigure(foo) with proper image
        while True:
            match = re.search(r"HelpFigure\(([^)]+)\)", html)
            if match:
                replacement = "<img src=\"%s/%s.png\" border=\"0\">" % (
                    media_path, match.group(1))
                html = html[0:match.start(0)] + replacement + \
                       html[match.end(0):]
            else:
                break
        # Related pages
        if self.related_pages:
            related_pages_html = "<h2>%s</h2>" % _("Related pages")
            related_pages_html += "<ul>"
            for page_id in self.related_pages:
                page = get_page(page_id)
                if page:
                    related_pages_html += "<li>"
                    related_pages_html += "<a href=\"page:%s\">%s</a>" % (page.id, page.header)
                    related_pages_html += "</li>"
            related_pages_html += "</ul>"
            html = html + related_pages_html
        return html


def get_page(id):
    return pages.get(id, None)


def get_pages_matching_search(search):
    search_words = search.split(" ")
    content_res = [r"\b%s\b" % x for x in search_words]
    matches = []
    for page in pages.values():
        match = True
        for content_re in content_res:
            if (not re.search(content_re, page.header, re.IGNORECASE) and
                not re.search(content_re, page.body, re.IGNORECASE)):
                match = False
                break
        if match:
            matches.append(page)
    return matches


def install_page(id, header="", body="", related_pages=[]):
    pages[id] = HelpPage(id, header, body, related_pages)


def show_page(page):
    gui_browser.show_page(page)
    gui_browser.Show()
    gui_browser.Raise()


def init(parent, home_page_param, media_path_param, page_modules):
    for page_module in page_modules:
        __import__(page_module)
    global gui_browser
    gui_browser = HelpBrowser(parent)
    global home_page
    home_page = home_page_param
    global media_path
    media_path = media_path_param


def _rst_to_html(rst):
    overrides = {"output_encoding": "unicode"}
    res = publish_parts(rst, writer_name="html", settings_overrides=overrides)
    body_html = res["html_body"]
    body_html = body_html.replace("<div class=\"document\">", "")
    body_html = body_html.replace("</div>", "")
    return body_html
