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


import logging
from datetime import datetime as dt

import wx

from timelinelib.db.interface import TimelineIOError
from timelinelib.db.interface import STATE_CHANGE_ANY
from timelinelib.drawing.interface import DrawingHints
from timelinelib.drawing.interface import EventRuntimeData
from timelinelib.drawing.utils import mult_timedelta
from timelinelib.drawing import get_drawer
from timelinelib.guinew.utils import sort_categories
from timelinelib.guinew.utils import _ask_question
from timelinelib.guinew.utils import _step_function
import timelinelib.config as config
import timelinelib.printing as printing


# Used by Sizer and Mover classes to detect when to go into action
HIT_REGION_PX_WITH = 5


class EventSizer(object):
    """Objects of this class are used to simplify resizing of events."""

    _singletons = {}
    _initialized = False
    
    def __new__(cls, *args, **kwds):
        """Implement the Singleton pattern for this class."""
        if cls not in cls._singletons:
            cls._singletons[cls] = super(EventSizer, cls).__new__(cls)
        return cls._singletons[cls]    
    
    def __init__(self, drawing_area, m_x = 0, m_y = 0):
        if not EventSizer._initialized:
            self.direction = wx.LEFT
            self.drawing_area = drawing_area
            self.metrics = self.drawing_area.drawing_algorithm.metrics
            self.sizing = False
            self.event = None
            EventSizer._initialized = True
        self.metrics = self.drawing_area.drawing_algorithm.metrics

    def sizing_starts(self, m_x, m_y):
        """
        If it is ok to start a resize... initialize the resize and return True.
        Otherwise return False.
        """
        self.sizing = (self._hit(m_x, m_y) and 
                       self.drawing_area.event_rt_data.is_selected(self.event))
        if self.sizing:
            self.x = m_x
            self.y = m_y
        return self.sizing

    def is_sizing(self):
        """Return True if we are in a resizing state, otherwise return False."""
        return self.sizing

    def set_cursor(self, m_x, m_y):
        """
        Used in mouse-move events to set the size cursor before the left mouse
        button is pressed, to indicate that a resize is possible (if it is!).
        Return True if the size-indicator-cursor is set, otherwise return False.
        """
        hit = self._hit(m_x, m_y)
        if hit:
            is_selected = self.drawing_area.event_rt_data.is_selected(self.event)
            if not is_selected:
                return False
            self.drawing_area._set_size_cursor()
        else:
            self.drawing_area._set_default_cursor()
        return hit

    def _hit(self, m_x, m_y):
        """
        Calculate the 'hit-for-resize' coordinates and return True if
        the mouse is within this area. Otherwise return False.
        The 'hit-for-resize' area is the are at the left and right edges of the
        event rectangle with a width of HIT_REGION_PX_WITH.
        """
        event_info = self.drawing_area.drawing_algorithm.event_with_rect_at(m_x, m_y)
        if event_info == None:
            return False
        self.event, rect = event_info
        if abs(m_x - rect.X) < HIT_REGION_PX_WITH:
            self.direction = wx.LEFT
            return True
        elif abs(rect.X + rect.Width - m_x) < HIT_REGION_PX_WITH:
            self.direction = wx.RIGHT
            return True
        return False

    def resize(self, m_x, m_y):
        """
        Resize the event either on the left or the right side.
        The event edge is snapped to the grid.
        """
        time = self.metrics.get_time(m_x)
        time = self.drawing_area.drawing_algorithm.snap(time)
        resized = False
        if self.direction == wx.LEFT:
            resized = self.event.update_start(time)
        else:
            resized = self.event.update_end(time)
        if resized:
            self.drawing_area._redraw_timeline()

class EventMover(object):
    """Objects of this class are used to simplify moving of events."""

    _singletons = {}
    _initialized = False
    
    def __new__(cls, *args, **kwds):
        """Implement the Singleton pattern for this class."""
        if cls not in cls._singletons:
            cls._singletons[cls] = super(EventMover, cls).__new__(cls)
        return cls._singletons[cls]    
    
    def __init__(self, drawing_area):
        """Initialize only the first time the class constructor is called."""
        if not EventMover._initialized:
            self.drawing_area = drawing_area
            self.drawing_algorithm = self.drawing_area.drawing_algorithm
            self.moving = False
            self.event = None
            EventMover._initialized = True

    def move_starts(self, m_x, m_y):
        """
        If it is ok to start a move... initialize the move and return True.
        Otherwise return False.
        """
        self.moving = (self._hit(m_x, m_y) and 
                       self.drawing_area.event_rt_data.is_selected(self.event))
        if self.moving:
            self.x = m_x
            self.y = m_y
        return self.moving
        
    def is_moving(self):
        """Return True if we are in a moving state, otherwise return False."""
        return self.moving

    def set_cursor(self, m_x, m_y):
        """
        Used in mouse-move events to set the move cursor before the left mouse
        button is pressed, to indicate that a move is possible (if it is!).
        Return True if the move-indicator-cursor is set, otherwise return False.
        """
        hit = self._hit(m_x, m_y)
        if hit:
            is_selected = self.drawing_area.event_rt_data.is_selected(self.event) 
            if not is_selected:
                return False
            self.drawing_area._set_move_cursor()
        else:
            self.drawing_area._set_default_cursor()
        return hit

    def move(self, m_x, m_y):
        """
        Move the event the time distance, difftime, represented by the distance the
        mouse has moved since the last move (m_x - self.x).
        Events found above the center line are snapped to the grid.
        """
        difftime = self.drawing_algorithm.metrics.get_difftime(m_x, self.x)
        # Snap events found above the center line
        start = self.event.time_period.start_time + difftime
        end = self.event.time_period.end_time + difftime
        if not self.drawing_algorithm.event_is_period(self.event.time_period):
            halfperiod = (end - start) / 2
            middletime = self.drawing_algorithm.snap(start + halfperiod)
            start = middletime - halfperiod
            end = middletime + halfperiod
        else:
            width = start - end
            startSnapped = self.drawing_area.drawing_algorithm.snap(start)
            endSnapped = self.drawing_area.drawing_algorithm.snap(end)
            if startSnapped != start:
                # Prefer to snap at left edge (in case end snapped as well)
                start = startSnapped
                end = start - width
            elif endSnapped != end:
                end = endSnapped
                start = end + width
        # Update and redraw the event
        self.event.update_period(start, end)
        self.drawing_area._redraw_timeline()
        # Adjust the coordinates  to get a smooth movement of cursor and event.
        # We can't use event_with_rect_at() method to get hold of the rect since
        # events can jump over each other when moved.
        rect = self.drawing_algorithm.event_rect(self.event)
        if rect != None:
            self.x = rect.X + rect.Width / 2
        else:
            self.x = m_x
        self.y = m_y

    def _hit(self, m_x, m_y):
        """
        Calculate the 'hit-for-move' coordinates and return True if
        the mouse is within this area. Otherwise return False.
        The 'hit-for-move' area is the are at the center of an event
        with a width of 2 * HIT_REGION_PX_WITH.
        """
        event_info = self.drawing_area.drawing_algorithm.event_with_rect_at(m_x, m_y)
        if event_info == None:
            return False
        self.event, rect = event_info
        center = rect.X + rect.Width / 2
        if abs(m_x - center) <= HIT_REGION_PX_WITH:
            return True
        return False

class DrawingArea(wx.Panel):
    """
    The right part in TimelinePanel: a window on which the timeline is drawn.

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

    def __init__(self, parent, divider_line_slider):
        wx.Panel.__init__(self, parent, style=wx.NO_BORDER)
        self.divider_line_slider = divider_line_slider
        self._create_gui()
        self._set_initial_values_to_member_variables()
        self._set_colors_and_styles()
        self.timeline = None
        self.printData = wx.PrintData()
        self.printData.SetPaperId(wx.PAPER_A4)
        self.printData.SetPrintMode(wx.PRINT_MODE_PRINTER)
        self.printData.SetOrientation(wx.LANDSCAPE)
        self.event_rt_data = EventRuntimeData()
        logging.debug("Init done in DrawingArea")

    def print_timeline(self, event):
        pdd = wx.PrintDialogData(self.printData)
        pdd.SetToPage(1)
        printer = wx.Printer(pdd)
        printout = printing.TimelinePrintout(self, False)
        frame = wx.GetApp().GetTopWindow()
        if not printer.Print(frame, printout, True):
            if printer.GetLastError() == wx.PRINTER_ERROR:
                wx.MessageBox(_("There was a problem printing.\nPerhaps your current printer is not set correctly?"), _("Printing"), wx.OK)
        else:
            self.printData = wx.PrintData( printer.GetPrintDialogData().GetPrintData() )
        printout.Destroy()

    def print_preview(self, event):
        data = wx.PrintDialogData(self.printData)
        printout_preview  = printing.TimelinePrintout(self, True)
        printout = printing.TimelinePrintout(self, False)
        self.preview = wx.PrintPreview(printout_preview, printout, data)
        if not self.preview.Ok():
            logging.debug("Problem with preview dialog...\n")
            return
        frame = wx.GetApp().GetTopWindow()
        pfrm = wx.PreviewFrame(self.preview, frame, _("Print preview"))
        pfrm.Initialize()
        pfrm.SetPosition(frame.GetPosition())
        pfrm.SetSize(frame.GetSize())
        pfrm.Show(True)

    def print_setup(self, event):
        psdd = wx.PageSetupDialogData(self.printData)
        psdd.CalculatePaperSizeFromId()
        dlg = wx.PageSetupDialog(self, psdd)
        dlg.ShowModal()
        # this makes a copy of the wx.PrintData instead of just saving
        # a reference to the one inside the PrintDialogData that will
        # be destroyed when the dialog is destroyed
        self.printData = wx.PrintData( dlg.GetPageSetupData().GetPrintData() )
        dlg.Destroy()

    def set_timeline(self, timeline):
        """Inform what timeline to draw."""
        if self.timeline != None:
            self.timeline.unregister(self._timeline_changed)
        self.timeline = timeline
        if self.timeline:
            self.timeline.register(self._timeline_changed)
            try:
                self.time_period = timeline.get_preferred_period()
            except TimelineIOError, e:
                wx.GetTopLevelParent(self).handle_timeline_error(e)
                return
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
        self.Bind(wx.EVT_RIGHT_DOWN, self._window_on_right_down)
        self.Bind(wx.EVT_LEFT_DCLICK, self._window_on_left_dclick)
        self.Bind(wx.EVT_LEFT_UP, self._window_on_left_up)
        self.Bind(wx.EVT_MOTION, self._window_on_motion)
        self.Bind(wx.EVT_MOUSEWHEEL, self._window_on_mousewheel)
        self.Bind(wx.EVT_KEY_DOWN, self._window_on_key_down)
        self.Bind(wx.EVT_KEY_UP, self._window_on_key_up)
        self.divider_line_slider.Bind(wx.EVT_SLIDER, self._slider_on_slider)
        self.divider_line_slider.Bind(wx.EVT_CONTEXT_MENU,
                                      self._slider_on_context_menu)

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
        try:
            logging.debug("Left mouse pressed event in DrawingArea")
            self._set_new_current_time(evt.m_x)
            # If we hit the event resize area of an event, start resizing
            if EventSizer(self).sizing_starts(evt.m_x, evt.m_y):
                return
            # If we hit the event move area of an event, start moving
            if EventMover(self).move_starts(evt.m_x, evt.m_y):
                return
            # No resizing or moving of events...
            if not self.timeline.is_read_only():
                posAtEvent = self._toggle_event_selection(evt.m_x, evt.m_y,
                                                          evt.m_controlDown)
                if not posAtEvent:
                    if evt.m_controlDown:
                        self._set_select_period_cursor()
            evt.Skip()
        except TimelineIOError, e:
            wx.GetTopLevelParent(self).handle_timeline_error(e)

    def _window_on_right_down(self, evt):
        """
        Event handler used when the right mouse button has been pressed.

        If the mouse hits an event and the timeline is not readonly, the 
        context menu for that event is displayed.
        """
        if self.timeline.is_read_only():
            return
        self.context_menu_event = self.drawing_algorithm.event_at(evt.m_x, evt.m_y)
        if self.context_menu_event == None:
            return
        menu_definitions = (
            ("Edit", self._context_menu_on_edit_event),
            ("Delete", self._context_menu_on_delete_event),
        )
        menu = wx.Menu()
        for menu_definition in menu_definitions:
            text, method = menu_definition
            menu_item = wx.MenuItem(menu, wx.NewId(), text)
            self.Bind(wx.EVT_MENU, method, id=menu_item.GetId())
            menu.AppendItem(menu_item)
        self.PopupMenu(menu)
        menu.Destroy()
        
    def _context_menu_on_edit_event(self, evt):
        frame = wx.GetTopLevelParent(self)
        frame.edit_event(self.context_menu_event)
        
    def _context_menu_on_delete_event(self, evt):
        self.context_menu_event.selected = True
        self._delete_selected_events()
    
    def _window_on_left_dclick(self, evt):
        """
        Event handler used when the left mouse button has been double clicked.

        If the timeline is readonly, no action is taken.
        If the mouse hits an event, a dialog opens for editing this event. 
        Otherwise a dialog for creating a new event is opened.
        """
        logging.debug("Left Mouse doubleclicked event in DrawingArea")
        if self.timeline.is_read_only():
            return
        # Since the event sequence is, 1. EVT_LEFT_DOWN  2. EVT_LEFT_UP
        # 3. EVT_LEFT_DCLICK we must compensate for the toggle_event_selection
        # that occurs in the handling of EVT_LEFT_DOWN, since we still want
        # the event(s) selected or deselected after a left doubleclick
        # It doesn't look too god but I havent found any other way to do it.
        self._toggle_event_selection(evt.m_x, evt.m_y, evt.m_controlDown)
        event = self.drawing_algorithm.event_at(evt.m_x, evt.m_y)
        if event:
            wx.GetTopLevelParent(self).edit_event(event)
        else:
            wx.GetTopLevelParent(self).create_new_event(self._current_time,
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
        if evt.m_leftDown:
            self._mouse_drag(evt.m_x, evt.m_y, evt.m_controlDown)
        else:
            if not evt.m_controlDown:
                self._mouse_move(evt.m_x, evt.m_y)                
                
    def _mouse_drag(self, x, y, ctrl=False):
        """
        The mouse has been moved.
        The left mouse button is depressed
        ctrl indicates if the Ctrl-key is depressed or not
        """
        if self.is_scrolling:
            self._scroll(x)
        elif self.is_selecting:
            self._mark_selected_minor_strips(x)
        # Resizing is only allowed if timeline is not readonly    
        elif EventSizer(self).is_sizing() and not self.timeline.is_read_only():
            EventSizer(self).resize(x, y)
        # Moving is only allowed if timeline is not readonly    
        elif EventMover(self).is_moving() and not self.timeline.is_read_only():
            EventMover(self).move(x, y)
        else:
            # Marking strips is only allowed if timeline is not readonly    
            if ctrl and not self.timeline.is_read_only():
                self._mark_selected_minor_strips(x)
                self.is_selecting = True
            else:
                self._scroll(x)
                self.is_scrolling = True
    
    def _mouse_move(self, x, y):
        """
        The mouse has been moved.
        The left mouse button is not depressed
        The Ctrl-key is not depressed
        """
        self._display_balloon_on_hoover(x, y)
        self._display_eventinfo_in_statusbar(x, y)
        cursor_set = EventSizer(self).set_cursor(x, y)
        if not cursor_set:
            EventMover(self).set_cursor(x, y)
                
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
            delta = mult_timedelta(self.time_period.delta(), direction / 10.0)
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

    def _slider_on_slider(self, evt):
        """The divider-line slider has been moved."""
        self._redraw_timeline()

    def _slider_on_context_menu(self, evt):
        """A right click has occured in the divider-line slider."""
        menu = wx.Menu()
        menu_item = wx.MenuItem(menu, wx.NewId(), _("Center"))
        self.Bind(wx.EVT_MENU, self._context_menu_on_menu_center,
                  id=menu_item.GetId())
        menu.AppendItem(menu_item)
        self.PopupMenu(menu)
        menu.Destroy()

    def _context_menu_on_menu_center(self, evt):
        """The 'Center' context menu has been selected."""
        self.divider_line_slider.SetValue(50)
        self._redraw_timeline()

    def _timeline_changed(self, state_change):
        if state_change == STATE_CHANGE_ANY:
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
        show_balloons_on_hover Show ballons on mouse hoover without clicking
        """
        self._current_time = None
        self._mark_selection = False
        self.bgbuf = None
        self.timeline = None
        self.time_period = None
        self.drawing_algorithm = get_drawer()
        self.is_scrolling = False
        self.is_selecting = False
        self.show_legend = config.get_show_legend()
        self.show_balloons_on_hover = config.get_balloon_on_hover()

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
                try:
                    settings = DrawingHints()
                    settings.period_selection = period_selection
                    settings.draw_legend = self.show_legend
                    settings.divider_position = (
                        self.divider_line_slider.GetValue())
                    settings.divider_position = (
                        float(self.divider_line_slider.GetValue()) / 100.0)
                    self.drawing_algorithm.draw(memdc, self.time_period,
                                                self.timeline,
                                                settings,
                                                self.event_rt_data)
                except TimelineIOError, e:
                    wx.GetTopLevelParent(self).handle_timeline_error(e)
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
        events will stay selected. If the Control key is not down all other
        events will be unselected.

        If the given position isn't within an event all selected events will
        be unselected.

        Return True if the given position was within an event, otherwise
        return False.
        """
        event = self.drawing_algorithm.event_at(xpixelpos, ypixelpos)
        if event:
            selected = not self.event_rt_data.is_selected(event)
            if not control_down:
                self.event_rt_data.clear_selected()
            self.event_rt_data.set_selected(event, selected)
        else:
            self.event_rt_data.clear_selected()
        self._redraw_timeline()
        return event != None

    def _end_selection_and_create_event(self, current_x):
        self._mark_selection = False
        period_selection = self._get_period_selection(current_x)
        start, end = period_selection
        wx.GetTopLevelParent(self).create_new_event(start, end)
        self._redraw_timeline()

    def _display_eventinfo_in_statusbar(self, xpixelpos, ypixelpos):
        """
        If the given position is within the boundaries of an event, the name of
        that event will be displayed in the status bar, otherwise the status
        bar text will be removed.
        """
        event = self.drawing_algorithm.event_at(xpixelpos, ypixelpos)
        if event != None:
            self._display_text_in_statusbar(event.get_label())
        else:
            self._reset_text_in_statusbar()
            
    def _display_balloon_on_hoover(self, xpixelpos, ypixelpos):
        event = self.drawing_algorithm.event_at(xpixelpos, ypixelpos)
        if self.show_balloons_on_hover:
            if event and not self.event_rt_data.is_selected(event):
                self.event_just_hoverd = event    
                self.timer = wx.Timer(self, -1)
                self.Bind(wx.EVT_TIMER, self.on_balloon_timer, self.timer)
                self.timer.Start(milliseconds=500, oneShot=True)
            else:
                self.event_just_hoverd = None
                self.redraw_balloons(None)
                
    def on_balloon_timer(self, event):
        self.redraw_balloons(self.event_just_hoverd)
   
    def redraw_balloons(self, event):
        if event:
            self.event_rt_data.set_balloon(event)
        else:    
            self.event_rt_data.clear_balloons()
        self._redraw_timeline()
        
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
        selected_event_ids = self.event_rt_data.get_selected_event_ids()
        nbr_of_selected_event_ids = len(selected_event_ids)
        if nbr_of_selected_event_ids > 1:
            text = _("Are you sure to delete %d events?" % 
                     nbr_of_selected_event_ids)
        else:
            text = _("Are you sure to delete?")
        if _ask_question(text, self) == wx.YES:
            try:
                for event_id in selected_event_ids:
                    self.timeline.delete_event(event_id)
            except TimelineIOError, e:
                wx.GetTopLevelParent(self).handle_timeline_error(e)

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

    def _set_size_cursor(self):
        self.SetCursor(wx.StockCursor(wx.CURSOR_SIZEWE))

    def _set_move_cursor(self):
        self.SetCursor(wx.StockCursor(wx.CURSOR_SIZING))

    def _set_default_cursor(self):
        """
        Set the cursor to it's default shape when it is in the timeline
        drawing area.
        """
        self.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))

    def balloon_visibility_changed(self, visible):
        self.show_balloons_on_hover = visible
        # When display on hovering is disabled we have to make sure 
        # that any visible balloon is removed.
        if not visible:
            self.drawing_algorithm.notify_events(
                            1, None)
            self._redraw_timeline()
