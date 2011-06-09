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


import time

import wx

from timelinelib.db.interface import STATE_CHANGE_ANY
from timelinelib.db.interface import TimelineIOError
from timelinelib.db.objects import TimeOutOfRangeLeftError
from timelinelib.db.objects import TimeOutOfRangeRightError
from timelinelib.db.objects import TimePeriod
from timelinelib.drawing import get_drawer
from timelinelib.drawing.interface import ViewProperties
from timelinelib.utils import ex_msg
from timelinelib.view.inputhandler import InputHandler
from timelinelib.view.noop import NoOpInputHandler
from timelinelib.view.resize import ResizeByDragInputHandler
from timelinelib.view.scrollbase import ScrollViewInputHandler
from timelinelib.wxgui.utils import _ask_question
from timelinelib.wxgui.utils import _step_function


# The width in pixels of the vertical scroll zones.
# When the mouse reaches the any of the two scroll zone areas, scrolling 
# of the timeline will take place if there is an ongoing selection of the 
# timeline. The scroll zone areas are found at the beginning and at the
# end of the timeline.
SCROLL_ZONE_WIDTH = 20

LEFT_RIGHT_SCROLL_FACTOR = 1 / 200.0
MOUSE_SCROLL_FACTOR = 1 / 10.0


class DrawingArea(wx.Panel):

    def __init__(self, parent, status_bar_adapter, divider_line_slider,
                 fn_handle_db_error, config):
        wx.Panel.__init__(self, parent, style=wx.NO_BORDER)
        self.controller = DrawingAreaController(
            self, status_bar_adapter, config, get_drawer(),
            divider_line_slider, fn_handle_db_error)
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

    def edit_event(self, event):
        wx.GetTopLevelParent(self).edit_event(event)

    def duplicate_event(self, event):
        wx.GetTopLevelParent(self).duplicate_event(event)

    def create_new_event(self, start_time, end_time):
        wx.GetTopLevelParent(self).create_new_event(start_time, end_time)

    def start_balloon_show_timer(self, milliseconds=-1, oneShot=False):
        self.balloon_show_timer.Start(milliseconds, oneShot)

    def start_balloon_hide_timer(self, milliseconds=-1, oneShot=False):
        self.balloon_hide_timer.Start(milliseconds, oneShot)

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
        self.balloon_show_timer = wx.Timer(self, -1)
        self.balloon_hide_timer = wx.Timer(self, -1)
        self.dragscroll_timer = wx.Timer(self, -1)
        self.Bind(wx.EVT_TIMER,            self._on_balloon_show_timer, self.balloon_show_timer)
        self.Bind(wx.EVT_TIMER,            self._on_balloon_hide_timer, self.balloon_hide_timer)
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

    def _on_balloon_show_timer(self, evt):
        self.controller.balloon_show_timer_fired()

    def _on_balloon_hide_timer(self, evt):
        self.controller.balloon_hide_timer_fired()

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
        self.controller.key_down(evt.GetKeyCode(), evt.AltDown())
        evt.Skip()

    def _on_key_up(self, evt):
        self.controller.key_up(evt.GetKeyCode())


class DrawingAreaController(object):

    def __init__(self, view, status_bar_adapter, config, drawing_algorithm,
                 divider_line_slider, fn_handle_db_error):
        self.config = config
        self.view = view
        self.status_bar_adapter = status_bar_adapter
        self.drawing_algorithm = drawing_algorithm
        self.divider_line_slider = divider_line_slider
        self.fn_handle_db_error = fn_handle_db_error
        self._set_initial_values_to_member_variables()
        self._set_colors_and_styles()
        self.divider_line_slider.Bind(wx.EVT_SLIDER,       self._slider_on_slider)
        self.divider_line_slider.Bind(wx.EVT_CONTEXT_MENU, self._slider_on_context_menu)
        self.change_input_handler_to_no_op()
        self.fast_draw = False

    def change_input_handler_to_zoom_by_drag(self, start_time):
        self.input_handler = ZoomByDragInputHandler(self, self.status_bar_adapter, start_time)

    def change_input_handler_to_create_period_event_by_drag(self, initial_time):
        self.input_handler = CreatePeriodEventByDragInputHandler(self, self.view, initial_time)

    def change_input_handler_to_resize_by_drag(self, event, direction):
        self.input_handler = ResizeByDragInputHandler(
            self, self.status_bar_adapter, event, direction)

    def change_input_handler_to_move_by_drag(self, event, start_drag_time):
        self.input_handler = MoveByDragInputHandler(self, event, start_drag_time)

    def change_input_handler_to_scroll_by_drag(self, start_time):
        self.input_handler = ScrollByDragInputHandler(self, start_time)

    def change_input_handler_to_no_op(self):
        self.input_handler = NoOpInputHandler(self, self.view)

    def get_drawer(self):
        return self.drawing_algorithm

    def get_timeline(self):
        return self.timeline

    def get_view_properties(self):
        return self.view_properties

    def set_timeline(self, timeline):
        """Inform what timeline to draw."""
        self._unregister_timeline(self.timeline)
        if timeline is None:
            self._set_null_timeline()
        else:
            self._set_non_null_timeline(timeline)

    def use_fast_draw(self, value):
        self.fast_draw = value
        
    def _set_null_timeline(self):
        self.timeline = None
        self.time_type = None
        self.view.Disable()
        
    def _set_non_null_timeline(self, timeline):
        self.timeline = timeline
        self.time_type = timeline.get_time_type()
        self.timeline.register(self._timeline_changed)
        properties_loaded = self._load_view_properties()
        if properties_loaded:
            self._redraw_timeline()
            self.view.Enable()
            self.view.SetFocus()

    def _load_view_properties(self):
        properties_loaded = True
        try:
            self.view_properties.clear_db_specific()
            self.timeline.load_view_properties(self.view_properties)
            if self.view_properties.displayed_period is None:
                default_tp = self.time_type.get_default_time_period()
                self.view_properties.displayed_period = default_tp
        except TimelineIOError, e:
            self.fn_handle_db_error(e)
            properties_loaded = False
        return properties_loaded
        
    def _unregister_timeline(self, timeline):
        if timeline != None:
            timeline.unregister(self._timeline_changed)

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
            self.status_bar_adapter.set_text("")
        except (TimeOutOfRangeLeftError), e:
            self.status_bar_adapter.set_text(_("Can't scroll more to the left"))
        except (TimeOutOfRangeRightError), e:
            self.status_bar_adapter.set_text(_("Can't scroll more to the right"))
        except (ValueError, OverflowError), e:
            self.status_bar_adapter.set_text(ex_msg(e))

    def redraw_timeline(self):
        self._redraw_timeline()

    def window_resized(self):
        self._redraw_timeline()

    def left_mouse_down(self, x, y, ctrl_down, shift_down):
        self.input_handler.left_mouse_down(x, y, ctrl_down, shift_down)

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

    def _one_and_only_one_event_selected(self):
        selected_event_ids = self.view_properties.get_selected_event_ids()
        nbr_of_selected_event_ids = len(selected_event_ids)
        return nbr_of_selected_event_ids == 1

    def _get_first_selected_event(self):
        selected_event_ids = self.view_properties.get_selected_event_ids()
        if len(selected_event_ids) > 0:
            id = selected_event_ids[0]
            return self.timeline.find_event_with_id(id)
        return None 
        
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
            current_time = self.get_time(x)
            self.view.create_new_event(current_time, current_time)

    def get_time(self, x):
        return self.drawing_algorithm.get_time(x)

    def middle_mouse_clicked(self, x):
        self.navigate_timeline(lambda tp: tp.center(self.get_time(x)))

    def left_mouse_up(self):
        self.input_handler.left_mouse_up()

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
                self.left_mouse_up()

    def mouse_moved(self, x, y):
        self.input_handler.mouse_moved(x, y)
                
    def mouse_wheel_moved(self, rotation, ctrl_down, shift_down):
        direction = _step_function(rotation)
        if ctrl_down:
            self._zoom_timeline(direction)
        elif shift_down:
            self.divider_line_slider.SetValue(self.divider_line_slider.GetValue() + direction)
            self._redraw_timeline()
        else:
            self._scroll_timeline_view(direction)

    def key_down(self, keycode, alt_down):
        if keycode == wx.WXK_DELETE:
            self._delete_selected_events()
        elif alt_down:
            if keycode == wx.WXK_UP:
                self._move_event_vertically(up=True)
            elif keycode == wx.WXK_DOWN:
                self._move_event_vertically(up=False)
            elif keycode == wx.WXK_RIGHT:
                self._scroll_timeline_view_by_factor(LEFT_RIGHT_SCROLL_FACTOR)
            elif keycode == wx.WXK_LEFT:
                self._scroll_timeline_view_by_factor(-LEFT_RIGHT_SCROLL_FACTOR)

    def _move_event_vertically(self, up=True):
        if self._one_and_only_one_event_selected():
            selected_event = self._get_first_selected_event()
            (overlapping_event, direction) = self.drawing_algorithm.get_closest_overlapping_event(selected_event, 
                                                                                                  up=up) 
            if overlapping_event is None:
                return
            if direction > 0:
                self.timeline.place_event_after_event(selected_event, 
                                                      overlapping_event)
            else:
                self.timeline.place_event_before_event(selected_event, 
                                                       overlapping_event)
            self._redraw_timeline()
                
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

    def _redraw_timeline(self):
        def fn_draw(dc):
            try:
                self.drawing_algorithm.use_fast_draw(self.fast_draw)
                self.drawing_algorithm.draw(dc, self.timeline, self.view_properties, self.config)
            except TimelineIOError, e:
                self.fn_handle_db_error(e)
            finally:
                self.drawing_algorithm.use_fast_draw(False)
        if self.timeline:
            self.view_properties.divider_position = (self.divider_line_slider.GetValue())
            self.view_properties.divider_position = (float(self.divider_line_slider.GetValue()) / 100.0)
            self.view.redraw_surface(fn_draw)
            self.view.enable_disable_menus()
            self._display_hidden_event_count()

    def _display_hidden_event_count(self):
        text = _("%s events hidden") % self.drawing_algorithm.get_hidden_event_count()
        self.status_bar_adapter.set_hidden_event_count_text(text)

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
            self.status_bar_adapter.set_text(event.get_label())
        else:
            self.status_bar_adapter.set_text("")
            
    def balloon_show_timer_fired(self):
        self.input_handler.balloon_show_timer_fired()

    def balloon_hide_timer_fired(self):
        self.input_handler.balloon_hide_timer_fired()
    
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
        self.input_handler.dragscroll_timer_fired()

    def _scroll_timeline_view(self, direction):
        factor = direction * MOUSE_SCROLL_FACTOR
        self._scroll_timeline_view_by_factor(factor)

    def _scroll_timeline_view_by_factor(self, factor):
        time_period = self.view_properties.displayed_period
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


class ScrollByDragInputHandler(InputHandler):

    def __init__(self, controller, start_time):
        self.controller = controller
        self.start_time = start_time
        self.last_clock_time = time.clock()
        self.last_x = 0
        self.last_x_distance = 0
        self.speed_px_per_sec = 0
        self.INERTIAL_SCROLLING_SPEED_THRESHOLD = 200

    def mouse_moved(self, x, y):
        self._calculate_sped(x)
        self._scroll_timeline(x)
        
    def left_mouse_up(self):
        self.controller.change_input_handler_to_no_op()
        if self.controller.config.use_inertial_scrolling:
            if self.speed_px_per_sec > self.INERTIAL_SCROLLING_SPEED_THRESHOLD:
                self._inertial_scrolling()

    def _calculate_sped(self, x):
        MAX_SPEED = 10000
        self.last_x_distance = x - self.last_x
        self.last_x = x
        current_clock_time = time.clock()
        elapsed_clock_time = current_clock_time - self.last_clock_time
        if elapsed_clock_time == 0:
            self.speed_px_per_sec = MAX_SPEED
        else:
            self.speed_px_per_sec = min(MAX_SPEED, abs(self.last_x_distance / 
                                        elapsed_clock_time))
        self.last_clock_time = current_clock_time

    def _scroll_timeline(self, x):
        self.current_time = self.controller.get_time(x)
        delta = (self.current_time - self.start_time)
        self.controller._scroll_timeline(delta)
        
    def _inertial_scrolling(self):
        frame_time = self._calculate_frame_time()
        value_factor = self._calculate_scroll_factor() 
        inertial_func = (0.20, 0.15, 0.10, 0.10, 0.10, 0.08, 0.06, 0.06, 0.05)
        #inertial_func = (0.20, 0.15, 0.10, 0.10, 0.07, 0.05, 0.02, 0.05)
        self.controller.use_fast_draw(True)
        next_frame_time = time.clock()
        for value in inertial_func:
            self.controller._scroll_timeline_view(value * value_factor)
            next_frame_time += frame_time
            sleep_time = next_frame_time - time.clock()
            if sleep_time >= 0:
                time.sleep(sleep_time)
        self.controller.use_fast_draw(False)
        self.controller._redraw_timeline()
                     
    def _calculate_frame_time(self):
        MAX_FRAME_RATE = 26.0
        frames_per_second = (MAX_FRAME_RATE * self.speed_px_per_sec / 
                             (100 + self.speed_px_per_sec))
        frame_time = 1.0 / frames_per_second
        return frame_time
    
    def _calculate_scroll_factor(self):
        if self.current_time > self.start_time:
            direction = 1
        else:
            direction = -1
        scroll_factor = (direction * self.speed_px_per_sec / 
                        self.INERTIAL_SCROLLING_SPEED_THRESHOLD)
        return scroll_factor 

     
class MoveByDragInputHandler(ScrollViewInputHandler):

    def __init__(self, controller, event, start_drag_time):
        ScrollViewInputHandler.__init__(self, controller)
        self.controller = controller
        self.event = event
        self.event_start_time = event.time_period.start_time
        self.event_end_time = event.time_period.end_time
        self.start_drag_time = start_drag_time

    def mouse_moved(self, x, y):
        ScrollViewInputHandler.mouse_moved(self, x, y)
        self._move_event()

    def left_mouse_up(self):
        ScrollViewInputHandler.left_mouse_up(self)
        self.controller.change_input_handler_to_no_op()

    def view_scrolled(self):
        self._move_event()

    def _move_event(self):
        if self.event.locked:
            return
        current_time = self.controller.get_time(self.last_x)
        delta = current_time - self.start_drag_time
        new_start = self.event_start_time + delta
        new_end = self.event_end_time + delta
        self.event.time_period.update(new_start, new_end)
        if self.controller.get_drawer().event_is_period(self.event.time_period):
            self._snap()
        self.controller.redraw_timeline()

    def _snap(self):
        start = self.event.time_period.start_time
        end = self.event.time_period.end_time
        width = start - end
        startSnapped = self.controller.get_drawer().snap(start)
        endSnapped = self.controller.get_drawer().snap(end)
        if startSnapped != start:
            # Prefer to snap at left edge (in case end snapped as well)
            start = startSnapped
            end = start - width
        elif endSnapped != end:
            end = endSnapped
            start = end + width
        self.event.update_period(start, end)


class SelectPeriodByDragInputHandler(ScrollViewInputHandler):

    def __init__(self, controller, initial_time):
        ScrollViewInputHandler.__init__(self, controller)
        self.controller = controller
        self.initial_time = initial_time
        self.last_valid_time = initial_time
        self.current_time = initial_time

    def mouse_moved(self, x, y):
        ScrollViewInputHandler.mouse_moved(self, x, y)
        self._move_current_time()

    def view_scrolled(self):
        self._move_current_time()

    def _move_current_time(self):
        self.current_time = self.controller.get_time(self.last_x)
        try:
            period = self.get_current_period()
            self.last_valid_time = self.current_time
        except ValueError:
            period = self.get_last_valid_period()
        self.controller.view_properties.period_selection = (period.start_time, period.end_time)
        self.controller._redraw_timeline()

    def get_last_valid_period(self):
        return self._get_period(self.initial_time, self.last_valid_time)

    def get_current_period(self):
        return self._get_period(self.initial_time, self.current_time)

    def _get_period(self, t1, t2):
        if t1 > t2:
            start = t2
            end = t1
        else:
            start = t1
            end = t2
        return TimePeriod(
            self.controller.get_timeline().get_time_type(), 
            self.controller.get_drawer().snap(start),
            self.controller.get_drawer().snap(end))

    def left_mouse_up(self):
        ScrollViewInputHandler.left_mouse_up(self)
        self.controller.view_properties.period_selection = None
        self.end_action()
        self.controller.redraw_timeline()
        self.controller.change_input_handler_to_no_op()

    def end_action(self):
        raise Exception("end_action not implemented in subclass.")


class CreatePeriodEventByDragInputHandler(SelectPeriodByDragInputHandler):

    def __init__(self, controller, view, initial_time):
        SelectPeriodByDragInputHandler.__init__(self, controller, initial_time)
        self.view = view

    def end_action(self):
        period = self.get_last_valid_period()
        self.view.create_new_event(period.start_time, period.end_time)


class ZoomByDragInputHandler(SelectPeriodByDragInputHandler):

    def __init__(self, controller, status_bar_adapter, start_time):
        SelectPeriodByDragInputHandler.__init__(self, controller, start_time)
        self.controller = controller
        self.status_bar_adapter = status_bar_adapter
        self.status_bar_adapter.set_text(_("Select region to zoom into"))

    def mouse_moved(self, x, y):
        SelectPeriodByDragInputHandler.mouse_moved(self, x, y)
        try:
            p = self.get_current_period()
        except ValueError:
            self.status_bar_adapter.set_text(_("Region too long"))
        else:
            if p.delta() < p.time_type.get_min_zoom_delta()[0]:
                self.status_bar_adapter.set_text(_("Region too short"))
            else:
                self.status_bar_adapter.set_text("")

    def end_action(self):
        self.status_bar_adapter.set_text("")
        period = self.get_last_valid_period()
        start = period.start_time
        end = period.end_time
        delta = end - start
        if period.time_type.zoom_is_ok(delta):
            # Don't zoom in to less than an hour which upsets things.
            self.controller.navigate_timeline(lambda tp: tp.update(start, end))
