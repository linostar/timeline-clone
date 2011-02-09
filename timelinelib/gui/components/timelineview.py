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


import wx

from timelinelib.drawing.utils import Metrics
from timelinelib.db.interface import TimelineIOError
from timelinelib.db.interface import STATE_CHANGE_ANY
from timelinelib.db.objects import TimePeriod
from timelinelib.db.objects import time_period_center
from timelinelib.drawing.interface import ViewProperties
from timelinelib.drawing import get_drawer
from timelinelib.gui.utils import _ask_question
from timelinelib.gui.utils import _step_function
import timelinelib.config as config
import timelinelib.printing as printing
from timelinelib.utils import ex_msg


# Used by Sizer and Mover classes to detect when to go into action
HIT_REGION_PX_WITH = 5

# The width in pixels of the vertical scroll zones.
# When the mouse reaches the any of the two scroll zone areas, scrolling 
# of the timeline will take place if there is an ongoing selection of the 
# timeline. The scroll zone areas are found at the beginning and at the
# end of the timeline.
SCROLL_ZONE_WIDTH = 20

# dragscroll timer interval in milliseconds
DRAGSCROLL_TIMER_MSINTERVAL = 300


class DrawingArea(wx.Panel):

    def __init__(self, parent, status_bar_adapter, divider_line_slider, fn_handle_db_error):
        wx.Panel.__init__(self, parent, style=wx.NO_BORDER)
        self.controller = DrawingAreaController(
            self, config.global_config, get_drawer(), divider_line_slider,
            fn_handle_db_error)
        self.status_bar_adapter = status_bar_adapter
        self.surface_bitmap = None
        self._create_gui()

    def get_drawer(self):
        return self.controller.get_drawer()

    def get_timeline(self):
        return self.controller.get_timeline()

    def get_view_properties(self):
        return self.controller.get_view_properties()

    def get_current_image(self):
        return self.surface_bitmap

    def print_timeline(self, event):
        self.controller.print_timeline(event)

    def print_preview(self, event):
        self.controller.print_preview(event)

    def print_setup(self, event):
        self.controller.print_setup(event)

    def set_timeline(self, timeline):
        self.controller.set_timeline(timeline)

    def show_hide_legend(self, show):
        self.controller.show_hide_legend(show)

    def get_time_period(self):
        return self.controller.get_time_period()

    def navigate_timeline(self, navigation_fn):
        self.controller.navigate_timeline(navigation_fn)

    def redraw_timeline(self):
        self.controller.redraw_timeline()

    def balloon_visibility_changed(self, visible):
        self.controller.balloon_visibility_changed(visible)

    def redraw_surface(self, fn_draw):
        width, height = self.GetSizeTuple()
        self.surface_bitmap = wx.EmptyBitmap(width, height)
        memdc = wx.MemoryDC()
        memdc.SelectObject(self.surface_bitmap)
        memdc.BeginDrawing()
        memdc.SetBackground(wx.Brush(wx.WHITE, wx.SOLID))
        memdc.Clear()
        fn_draw(memdc)
        memdc.EndDrawing()
        del memdc
        self.Refresh()
        self.Update()

    def enable_disable_menus(self):
        wx.GetTopLevelParent(self).enable_disable_menus()

    def set_status_text(self, text):
        self.status_bar_adapter.set_text(text)

    def set_hidden_event_count_text(self, text):
        self.status_bar_adapter.set_hidden_event_count_text(text)

    def edit_event(self, event):
        wx.GetTopLevelParent(self).edit_event(event)

    def duplicate_event(self, event):
        wx.GetTopLevelParent(self).duplicate_event(event)

    def create_new_event(self, start_time, end_time):
        wx.GetTopLevelParent(self).create_new_event(start_time, end_time)

    def get_metrics(self):
        return self.controller.get_metrics()

    def start_balloon_timer1(self, milliseconds=-1, oneShot=False):
        self.balloon_timer1.Start(milliseconds, oneShot)

    def start_balloon_timer2(self, milliseconds=-1, oneShot=False):
        self.balloon_timer2.Start(milliseconds, oneShot)

    def start_dragscroll_timer(self, milliseconds=-1, oneShot=False):
        self.dragscroll_timer.Start(milliseconds, oneShot)

    def stop_dragscroll_timer(self):
        self.dragscroll_timer.Stop()

    def set_select_period_cursor(self):
        self.SetCursor(wx.StockCursor(wx.CURSOR_IBEAM))

    def set_size_cursor(self):
        self.SetCursor(wx.StockCursor(wx.CURSOR_SIZEWE))

    def set_move_cursor(self):
        self.SetCursor(wx.StockCursor(wx.CURSOR_SIZING))

    def set_default_cursor(self):
        self.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))

    def ask_question(self, question):
        return _ask_question(question, self)

    def _create_gui(self):
        self.balloon_timer1 = wx.Timer(self, -1)
        self.balloon_timer2 = wx.Timer(self, -1)
        self.dragscroll_timer = wx.Timer(self, -1)
        self.Bind(wx.EVT_TIMER,            self._on_balloon_timer1, self.balloon_timer1)
        self.Bind(wx.EVT_TIMER,            self._on_balloon_timer2, self.balloon_timer2)
        self.Bind(wx.EVT_TIMER,            self._on_dragscroll, self.dragscroll_timer)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self._on_erase_background)
        self.Bind(wx.EVT_PAINT,            self._on_paint)
        self.Bind(wx.EVT_SIZE,             self._on_size)
        self.Bind(wx.EVT_LEFT_DOWN,        self._on_left_down)
        self.Bind(wx.EVT_RIGHT_DOWN,       self._on_right_down)
        self.Bind(wx.EVT_LEFT_DCLICK,      self._on_left_dclick)
        self.Bind(wx.EVT_MIDDLE_UP,        self._on_middle_up)
        self.Bind(wx.EVT_LEFT_UP,          self._on_left_up)
        self.Bind(wx.EVT_ENTER_WINDOW,     self._on_enter)
        self.Bind(wx.EVT_MOTION,           self._on_motion)
        self.Bind(wx.EVT_MOUSEWHEEL,       self._on_mousewheel)
        self.Bind(wx.EVT_KEY_DOWN,         self._on_key_down)
        self.Bind(wx.EVT_KEY_UP,           self._on_key_up)

    def _on_balloon_timer1(self, evt):
        self.controller.balloon_timer1_fired()

    def _on_balloon_timer2(self, evt):
        self.controller.balloon_timer2_fired()

    def _on_dragscroll(self, evt):
        self.controller.dragscroll_timer_fired()

    def _on_erase_background(self, event):
        # For double buffering
        pass

    def _on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.BeginDrawing()
        if self.surface_bitmap:
            dc.DrawBitmap(self.surface_bitmap, 0, 0, True)
        else:
            pass # TODO: Fill with white?
        dc.EndDrawing()

    def _on_size(self, evt):
        self.controller.window_resized()

    def _on_left_down(self, evt):
        self.controller.left_mouse_down(evt.m_x, evt.m_y, evt.m_controlDown, evt.m_shiftDown)
        evt.Skip()

    def _on_right_down(self, evt):
        self.controller.right_mouse_down(evt.m_x, evt.m_y)

    def _on_left_dclick(self, evt):
        self.controller.left_mouse_dclick(evt.m_x, evt.m_y, evt.m_controlDown)

    def _on_middle_up(self, evt):
        self.controller.middle_mouse_clicked(evt.m_x)

    def _on_left_up(self, evt):
        self.controller.left_mouse_up()

    def _on_enter(self, evt):
        self.controller.mouse_enter(evt.m_x, evt.LeftIsDown())

    def _on_motion(self, evt):
        self.controller.mouse_moved(evt.m_x, evt.m_y)

    def _on_mousewheel(self, evt):
        self.controller.mouse_wheel_moved(evt.m_wheelRotation, evt.ControlDown(), evt.ShiftDown())

    def _on_key_down(self, evt):
        self.controller.key_down(evt.GetKeyCode())
        evt.Skip()

    def _on_key_up(self, evt):
        self.controller.key_up(evt.GetKeyCode())


class DrawingAreaController(object):

    def __init__(self, view, config, drawing_algorithm, divider_line_slider, fn_handle_db_error):
        self.config = config
        self.view = view
        self.drawing_algorithm = drawing_algorithm
        self.divider_line_slider = divider_line_slider
        self.fn_handle_db_error = fn_handle_db_error
        self._set_initial_values_to_member_variables()
        self._set_colors_and_styles()
        self.printData = wx.PrintData()
        self.printData.SetPaperId(wx.PAPER_A4)
        self.printData.SetPrintMode(wx.PRINT_MODE_PRINTER)
        self.printData.SetOrientation(wx.LANDSCAPE)
        self.divider_line_slider.Bind(wx.EVT_SLIDER,       self._slider_on_slider)
        self.divider_line_slider.Bind(wx.EVT_CONTEXT_MENU, self._slider_on_context_menu)
        self.change_input_handler(NoOpInputHandler())

    def change_input_handler(self, input_handler):
        self.input_handler = input_handler

    def get_drawer(self):
        return self.drawing_algorithm

    def get_timeline(self):
        return self.timeline

    def get_view_properties(self):
        return self.view_properties

    def print_timeline(self, event):
        pdd = wx.PrintDialogData(self.printData)
        pdd.SetToPage(1)
        printer = wx.Printer(pdd)
        printout = printing.TimelinePrintout(self.view, False)
        frame = wx.GetApp().GetTopWindow()
        if not printer.Print(frame, printout, True):
            if printer.GetLastError() == wx.PRINTER_ERROR:
                wx.MessageBox(_("There was a problem printing.\nPerhaps your current printer is not set correctly?"), _("Printing"), wx.OK)
        else:
            self.printData = wx.PrintData( printer.GetPrintDialogData().GetPrintData() )
        printout.Destroy()

    def print_preview(self, event):
        data = wx.PrintDialogData(self.printData)
        printout_preview  = printing.TimelinePrintout(self.view, True)
        printout = printing.TimelinePrintout(self.view, False)
        self.preview = wx.PrintPreview(printout_preview, printout, data)
        if not self.preview.Ok():
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
        dlg = wx.PageSetupDialog(self.view, psdd)
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
        self.time_type = None if timeline is None else self.timeline.get_time_type()
        if self.timeline:
            self.timeline.register(self._timeline_changed)
            try:
                self.view_properties.clear_db_specific()
                timeline.load_view_properties(self.view_properties)
                if self.view_properties.displayed_period is None:
                    default_tp = self.time_type.get_default_time_period()
                    self.view_properties.displayed_period = default_tp
            except TimelineIOError, e:
                self.fn_handle_db_error(e)
                return
            self._redraw_timeline()
            self.view.Enable()
            self.view.SetFocus()
        else:
            self.view.Disable()

    def show_hide_legend(self, show):
        self.view_properties.show_legend = show
        if self.timeline:
            self._redraw_timeline()

    def get_time_period(self):
        """Return currently displayed time period."""
        if self.timeline == None:
            raise Exception(_("No timeline set"))
        return self.view_properties.displayed_period

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
            navigation_fn(self.view_properties.displayed_period)
            self._redraw_timeline()
            self.view.set_status_text("")
        except (ValueError, OverflowError), e:
            self.view.set_status_text(ex_msg(e))

    def redraw_timeline(self):
        self._redraw_timeline()

    def window_resized(self):
        self._redraw_timeline()

    def left_mouse_down(self, x, y, ctrl_down, shift_down):
        self.input_handler.left_mouse_down(self, x, y, ctrl_down, shift_down)

    def right_mouse_down(self, x, y):
        """
        Event handler used when the right mouse button has been pressed.

        If the mouse hits an event and the timeline is not readonly, the 
        context menu for that event is displayed.
        """
        if self.timeline.is_read_only():
            return
        self.context_menu_event = self.drawing_algorithm.event_at(x, y)
        if self.context_menu_event is None:
            return
        menu_definitions = [
            (_("Edit"), self._context_menu_on_edit_event),
            (_("Duplicate..."), self._context_menu_on_duplicate_event),
            (_("Delete"), self._context_menu_on_delete_event),
        ]
        if self.context_menu_event.has_data():
            menu_definitions.append((_("Sticky Balloon"), self._context_menu_on_sticky_balloon_event))
        menu = wx.Menu()
        for menu_definition in menu_definitions:
            text, method = menu_definition
            menu_item = wx.MenuItem(menu, wx.NewId(), text)
            self.view.Bind(wx.EVT_MENU, method, id=menu_item.GetId())
            menu.AppendItem(menu_item)
        self.view.PopupMenu(menu)
        menu.Destroy()

    def _context_menu_on_edit_event(self, evt):
        self.view.edit_event(self.context_menu_event)

    def _context_menu_on_duplicate_event(self, evt):
        self.view.duplicate_event(self.context_menu_event)
        
    def _context_menu_on_delete_event(self, evt):
        self.context_menu_event.selected = True
        self._delete_selected_events()
        
    def _context_menu_on_sticky_balloon_event(self, evt):
        self.view_properties.set_event_has_sticky_balloon(self.context_menu_event, has_sticky=True)
        self._redraw_timeline()
    
    def left_mouse_dclick(self, x, y, ctrl_down):
        """
        Event handler used when the left mouse button has been double clicked.

        If the timeline is readonly, no action is taken.
        If the mouse hits an event, a dialog opens for editing this event. 
        Otherwise a dialog for creating a new event is opened.
        """
        if self.timeline.is_read_only():
            return
        # Since the event sequence is, 1. EVT_LEFT_DOWN  2. EVT_LEFT_UP
        # 3. EVT_LEFT_DCLICK we must compensate for the toggle_event_selection
        # that occurs in the handling of EVT_LEFT_DOWN, since we still want
        # the event(s) selected or deselected after a left doubleclick
        # It doesn't look too god but I havent found any other way to do it.
        self._toggle_event_selection(x, y, ctrl_down)
        event = self.drawing_algorithm.event_at(x, y)
        if event:
            self.view.edit_event(event)
        else:
            current_time = self.metrics.get_time(x)
            self.view.create_new_event(current_time, current_time)

    def middle_mouse_clicked(self, x):
        self.navigate_timeline(lambda tp: tp.center(self.get_metrics().get_time(x)))

    def left_mouse_up(self):
        self.input_handler.left_mouse_up(self)

    def mouse_enter(self, x, left_is_down):
        """
        Mouse event handler, when the mouse is entering the window.
        
        If there is an ongoing selection-marking (dragscroll timer running)
        and the left mouse button is not down when we enter the window, we 
        want to simulate a 'mouse left up'-event, so that the dialog for 
        creating an event will be opened or sizing, moving stops. 
        """
        if self.dragscroll_timer_running:
            if not left_is_down:
                self.left_mouse_up(x)

    def mouse_moved(self, x, y):
        self.input_handler.mouse_moved(self, x, y)
                
    def mouse_wheel_moved(self, rotation, ctrl_down, shift_down):
        direction = _step_function(rotation)
        if ctrl_down:
            self._zoom_timeline(direction)
        elif shift_down:
            self.divider_line_slider.SetValue(self.divider_line_slider.GetValue() + direction)
            self._redraw_timeline()
        else:
            self._scroll_timeline_view(direction)

    def key_down(self, keycode):
        if keycode == wx.WXK_DELETE:
            self._delete_selected_events()

    def key_up(self, keycode):
        if keycode == wx.WXK_CONTROL:
            self.view.set_default_cursor()

    def _slider_on_slider(self, evt):
        self._redraw_timeline()

    def _slider_on_context_menu(self, evt):
        """A right click has occured in the divider-line slider."""
        menu = wx.Menu()
        menu_item = wx.MenuItem(menu, wx.NewId(), _("Center"))
        self.view.Bind(wx.EVT_MENU, self._context_menu_on_menu_center,
                  id=menu_item.GetId())
        menu.AppendItem(menu_item)
        self.view.PopupMenu(menu)
        menu.Destroy()

    def _context_menu_on_menu_center(self, evt):
        """The 'Center' context menu has been selected."""
        self.divider_line_slider.SetValue(50)
        self._redraw_timeline()

    def _timeline_changed(self, state_change):
        if state_change == STATE_CHANGE_ANY:
            self._redraw_timeline()

    def _set_initial_values_to_member_variables(self):
        self.timeline = None
        self.view_properties = ViewProperties()
        self.view_properties.show_legend = self.config.get_show_legend()
        self.view_properties.show_balloons_on_hover = self.config.get_balloon_on_hover()
        self.dragscroll_timer_running = False
        
    def _set_colors_and_styles(self):
        """Define the look and feel of the drawing area."""
        self.view.SetBackgroundColour(wx.WHITE)
        self.view.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.view.set_default_cursor()
        self.view.Disable()

    def _redraw_timeline(self, period_selection=None):
        def fn_draw(dc):
            try:
                self.drawing_algorithm.draw(dc, self.timeline, self.view_properties)
            except TimelineIOError, e:
                self.fn_handle_db_error(e)
        if self.timeline:
            self.view_properties.period_selection = period_selection
            self.view_properties.divider_position = (self.divider_line_slider.GetValue())
            self.view_properties.divider_position = (float(self.divider_line_slider.GetValue()) / 100.0)
            self.metrics = Metrics(self.view.GetSizeTuple(), self.time_type, 
                                   self.view_properties.displayed_period, 
                                   self.view_properties.divider_position)
            self.view.redraw_surface(fn_draw)
            self.view.enable_disable_menus()
            self._display_hidden_event_count()

    def _display_hidden_event_count(self):
        text = _("%s events hidden") % self.drawing_algorithm.get_hidden_event_count()
        self.view.set_hidden_event_count_text(text)

    def _toggle_event_selection(self, xpixelpos, ypixelpos, control_down):
        event = self.drawing_algorithm.event_at(xpixelpos, ypixelpos)
        if event:
            selected = not self.view_properties.is_selected(event)
            if not control_down:
                self.view_properties.clear_selected()
            self.view_properties.set_selected(event, selected)
        else:
            self.view_properties.clear_selected()
        self._redraw_timeline()
        return event != None

    def _display_eventinfo_in_statusbar(self, xpixelpos, ypixelpos):
        event = self.drawing_algorithm.event_at(xpixelpos, ypixelpos)
        if event != None:
            self.view.set_status_text(event.get_label())
        else:
            self.view.set_status_text("")
            
    def balloon_timer1_fired(self):
        self.input_handler.balloon_timer1_fired(self)

    def balloon_timer2_fired(self):
        self.input_handler.balloon_timer2_fired(self)
    
    def _redraw_balloons(self, event):
        self.view_properties.hovered_event = event
        self._redraw_timeline()
        
    def _in_scroll_zone(self, x):
        """
        Return True if x is within the left hand or right hand area
        where timed scrolling shall start/continue.
        """
        width, height = self.view.GetSizeTuple()
        if width - x < SCROLL_ZONE_WIDTH or x < SCROLL_ZONE_WIDTH:
            return True
        return False
        
    def dragscroll_timer_fired(self):
        self.input_handler.dragscroll_timer_fired(self)

    def _scroll_timeline_view(self, direction):
        time_period = self.view_properties.displayed_period
        factor = direction / 10.0
        delta = self.time_type.mult_timedelta(time_period.delta(), factor) 
        self._scroll_timeline(delta)

    def _scroll_timeline(self, delta):
        self.navigate_timeline(lambda tp: tp.move_delta(-delta))

    def _zoom_timeline(self, direction=0):
        self.navigate_timeline(lambda tp: tp.zoom(direction))

    def _delete_selected_events(self):
        """After acknowledge from the user, delete all selected events."""
        selected_event_ids = self.view_properties.get_selected_event_ids()
        nbr_of_selected_event_ids = len(selected_event_ids)
        if nbr_of_selected_event_ids > 1:
            text = _("Are you sure you want to delete %d events?" % 
                     nbr_of_selected_event_ids)
        else:
            text = _("Are you sure you want to delete this event?")
        if self.view.ask_question(text) == wx.YES:
            try:
                for event_id in selected_event_ids:
                    self.timeline.delete_event(event_id)
            except TimelineIOError, e:
                self.fn_handle_db_error(e)

    def balloon_visibility_changed(self, visible):
        self.view_properties.show_balloons_on_hover = visible
        # When display on hovering is disabled we have to make sure 
        # that any visible balloon is removed.
        # TODO: Do we really need that?
        if not visible:
            self._redraw_timeline()

    def get_metrics(self):
        return self.metrics


class InputHandler(object):

    def left_mouse_down(self, controller, x, y, ctrl_down, shift_down):
        pass

    def mouse_moved(self, controller, x, y):
        pass

    def left_mouse_up(self, controller):
        pass

    def dragscroll_timer_fired(self, controller):
        pass

    def balloon_timer1_fired(self, controller):
        pass

    def balloon_timer2_fired(self, controller):
        pass


class NoOpInputHandler(InputHandler):

    def __init__(self):
        self.timer1_running = False
        self.timer2_running = False

    def left_mouse_down(self, controller, x, y, ctrl_down, shift_down):
        eventWithBalloon = controller.drawing_algorithm.balloon_at(x, y)
        if eventWithBalloon: 
            stick = not controller.view_properties.event_has_sticky_balloon(eventWithBalloon)
            controller.view_properties.set_event_has_sticky_balloon(eventWithBalloon, has_sticky=stick)
            if stick:
                controller._redraw_timeline()
            else:
                if controller.view_properties.show_balloons_on_hover:
                    controller._redraw_balloons(eventWithBalloon)
                else:
                    controller._redraw_balloons(None)
        event = controller.get_drawer().event_at(x, y)
        time_at_x = controller.get_metrics().get_time(x)
        if self._hit_resize_handle(controller, x, y) is not None:
            direction = self._hit_resize_handle(controller, x, y)
            controller.change_input_handler(ResizeByDragInputHandler(event, direction))
            return
        if self._hit_move_handle(controller, x, y):
            controller.change_input_handler(MoveByDragInputHandler(event, time_at_x))
            return
        if (event is None and ctrl_down == False and shift_down == False):
            controller._toggle_event_selection(x, y, ctrl_down)
            controller.change_input_handler(ScrollByDragInputHandler(time_at_x))
            return
        if (event is None and ctrl_down == True):
            controller._toggle_event_selection(x, y, ctrl_down)
            controller.change_input_handler(CreatePeriodEventByDragInputHandler(time_at_x))
            return
        if (event is None and shift_down == True):
            controller._toggle_event_selection(x, y, ctrl_down)
            controller.change_input_handler(ZoomByDragInputHandler(time_at_x))
            return
        controller._toggle_event_selection(x, y, ctrl_down)

    def mouse_moved(self, controller, x, y):
        self._display_balloon_on_hover(controller, x, y)
        controller._display_eventinfo_in_statusbar(x, y)
        if self._hit_resize_handle(controller, x, y) is not None:
            controller.view.set_size_cursor()
        elif self._hit_move_handle(controller, x, y):
            controller.view.set_move_cursor()
        else:
            controller.view.set_default_cursor()
        return

    def balloon_timer1_fired(self, controller):
        self.timer1_running = False
        controller._redraw_balloons(controller.current_event)

    def balloon_timer2_fired(self, controller):
        self.timer2_running = False
        hevt = controller.view_properties.hovered_event
        # If there is no balloon visible we don't have to do anything
        if hevt is None:
            return
        cevt = controller.current_event
        bevt = controller.balloon_event
        # If the visible balloon doesn't belong to the event pointed to
        # we remove the ballloon.
        if hevt != cevt and hevt != bevt: 
            controller._redraw_balloons(None)

    def _display_balloon_on_hover(self, controller, xpixelpos, ypixelpos):
        """
        Show or hide balloons depending on current situation.
           self.current_event: The event pointed to, or None
           self.balloon_event: The event that belongs to the balloon pointed
                               to, or None.
        """
        # The balloon functionality is not enabled
        if not controller.view_properties.show_balloons_on_hover:
            return
        controller.current_event = controller.drawing_algorithm.event_at(xpixelpos, ypixelpos)
        controller.balloon_event = controller.drawing_algorithm.balloon_at(xpixelpos, ypixelpos)
        # No balloon handling for selected events
        if controller.current_event and controller.view_properties.is_selected(controller.current_event):
            return
        # Timer-1 is running. We have to wait for it to finish before doing anything
        if self.timer1_running:
            return
        # Timer-2 is running. We have to wait for it to finish before doing anything
        if self.timer2_running:
            return
        # We are pointing to an event... 
        if controller.current_event is not None:
            # We are not pointing on a balloon...
            if controller.balloon_event is None:
                # We have no balloon, so we start Timer-1
                if controller.view_properties.hovered_event != controller.current_event:
                    #print "Timer-1 Started ", controller.current_event
                    controller.view.start_balloon_timer1(milliseconds=500, oneShot=True)
                    self.timer1_running = True
        # We are not pointing to any event....        
        else:
            # We have a balloon...
            if controller.view_properties.hovered_event is not None:
                # When we are moving within our 'own' balloon we dont't start Timer-2
                # Otherwise Timer-2 is started.
                if controller.balloon_event != controller.view_properties.hovered_event:
                    #print "Timer-2 Started"
                    controller.view.start_balloon_timer2(milliseconds=100, oneShot=True)

    def _hit_move_handle(self, controller, x, y):
        event_and_rect = controller.get_drawer().event_with_rect_at(x, y)
        if event_and_rect is None:
            return False
        event, rect = event_and_rect
        if not controller.get_view_properties().is_selected(event):
            return False
        center = rect.X + rect.Width / 2
        if abs(x - center) <= HIT_REGION_PX_WITH:
            return True
        return False

    def _hit_resize_handle(self, controller, x, y):
        event_and_rect = controller.get_drawer().event_with_rect_at(x, y)
        if event_and_rect == None:
            return None
        event, rect = event_and_rect
        if not controller.get_view_properties().is_selected(event):
            return None
        if abs(x - rect.X) < HIT_REGION_PX_WITH:
            return wx.LEFT
        elif abs(rect.X + rect.Width - x) < HIT_REGION_PX_WITH:
            return wx.RIGHT
        return None


class ScrollByDragInputHandler(InputHandler):

    def __init__(self, start_time):
        self.start_time = start_time

    def mouse_moved(self, controller, x, y):
        current_time = controller.get_metrics().get_time(x)
        delta = (current_time - self.start_time)
        controller._scroll_timeline(delta)

    def left_mouse_up(self, controller):
        controller.change_input_handler(NoOpInputHandler())


class ScrollViewInputHandler(InputHandler):

    def __init__(self):
        self.timer_running = False

    def mouse_moved(self, controller, x, y):
        self.last_x = x
        if controller._in_scroll_zone(x) and not self.timer_running:
            controller.view.start_dragscroll_timer(milliseconds=DRAGSCROLL_TIMER_MSINTERVAL)
            self.timer_running = True

    def left_mouse_up(self, controller):
        controller.view.stop_dragscroll_timer()

    def dragscroll_timer_fired(self, controller):
        if controller._in_scroll_zone(self.last_x):
            if self.last_x < SCROLL_ZONE_WIDTH:
                direction = 1
            else:
                direction = -1
            controller._scroll_timeline_view(direction)
            self.view_scrolled(controller)

    def view_scrolled(self, controller):
        raise Exception("view_scrolled not implemented in subclass.")


class MoveByDragInputHandler(ScrollViewInputHandler):

    def __init__(self, event, start_drag_time):
        ScrollViewInputHandler.__init__(self)
        self.event = event
        self.event_start_time = event.time_period.start_time
        self.event_end_time = event.time_period.end_time
        self.start_drag_time = start_drag_time

    def mouse_moved(self, controller, x, y):
        ScrollViewInputHandler.mouse_moved(self, controller, x, y)
        self._move_event(controller)

    def left_mouse_up(self, controller):
        ScrollViewInputHandler.left_mouse_up(self, controller)
        controller.change_input_handler(NoOpInputHandler())

    def view_scrolled(self, controller):
        self._move_event(controller)

    def _move_event(self, controller):
        current_time = controller.get_metrics().get_time(self.last_x)
        delta = current_time - self.start_drag_time
        new_start = self.event_start_time + delta
        new_end = self.event_end_time + delta
        self.event.time_period.update(new_start, new_end)
        if controller.get_drawer().event_is_period(self.event.time_period):
            self._snap(controller)
        controller.redraw_timeline()

    def _snap(self, controller):
        start = self.event.time_period.start_time
        end = self.event.time_period.end_time
        width = start - end
        startSnapped = controller.get_drawer().snap(start)
        endSnapped = controller.get_drawer().snap(end)
        if startSnapped != start:
            # Prefer to snap at left edge (in case end snapped as well)
            start = startSnapped
            end = start - width
        elif endSnapped != end:
            end = endSnapped
            start = end + width
        self.event.update_period(start, end)


class ResizeByDragInputHandler(ScrollViewInputHandler):

    def __init__(self, event, direction):
        ScrollViewInputHandler.__init__(self)
        self.event = event
        self.direction = direction
        self.timer_running = False

    def mouse_moved(self, controller, x, y):
        ScrollViewInputHandler.mouse_moved(self, controller, x, y)
        self._resize_event(controller)

    def left_mouse_up(self, controller):
        ScrollViewInputHandler.left_mouse_up(self, controller)
        controller.change_input_handler(NoOpInputHandler())

    def view_scrolled(self, controller):
        self._resize_event(controller)

    def _resize_event(self, controller):
        new_time = controller.get_metrics().get_time(self.last_x)
        new_snapped_time = controller.get_drawer().snap(new_time)
        if self.direction == wx.LEFT:
            new_start = new_snapped_time
            new_end = self.event.time_period.end_time
            if new_start > new_end:
                new_start = new_end
        else:
            new_start = self.event.time_period.start_time
            new_end = new_snapped_time
            if new_end < new_start:
                new_end = new_start
        self.event.update_period(new_start, new_end)
        controller.redraw_timeline()


class SelectPeriodByDragInputHandler(ScrollViewInputHandler):

    def __init__(self, start_time):
        ScrollViewInputHandler.__init__(self)
        self.start_time = start_time
        self.end_time = start_time

    def mouse_moved(self, controller, x, y):
        ScrollViewInputHandler.mouse_moved(self, controller, x, y)
        self._move_end_time(controller)

    def left_mouse_up(self, controller):
        ScrollViewInputHandler.left_mouse_up(self, controller)
        self.end_action(controller, self._get_period(controller))
        controller.redraw_timeline()
        controller.change_input_handler(NoOpInputHandler())

    def view_scrolled(self, controller):
        self._move_end_time(controller)

    def _get_period(self, controller):
        start = self.start_time
        end = self.end_time
        if self.start_time > self.end_time:
            start = self.end_time
            end = self.start_time
        return TimePeriod(controller.get_timeline().get_time_type(), 
                          controller.get_drawer().snap(start),
                          controller.get_drawer().snap(end))

    def _move_end_time(self, controller):
        self.end_time = controller.get_metrics().get_time(self.last_x)
        period = self._get_period(controller)
        start = period.start_time
        end = period.end_time
        controller._redraw_timeline((start, end))

    def end_action(self, controller, period):
        raise Exception("end_action not implemented in subclass.")


class CreatePeriodEventByDragInputHandler(SelectPeriodByDragInputHandler):

    def end_action(self, controller, period):
        controller.view.create_new_event(period.start_time, period.end_time)


class ZoomByDragInputHandler(SelectPeriodByDragInputHandler):

    def end_action(self, controller, period):
        start = period.start_time
        end = period.end_time
        delta = end - start
        if period.time_type.zoom_is_ok(delta):
            # Don't zoom in to less than an hour which upsets things.
            controller.navigate_timeline(lambda tp: tp.update(start, end))
