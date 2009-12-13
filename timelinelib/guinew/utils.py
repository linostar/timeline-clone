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
Utility functions for working with GUI.
"""


import wx


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
