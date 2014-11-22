Crash reports
=============

TypeError: not all arguments converted during string formatting
---------------------------------------------------------------

Reported 16 November 2014::

    Traceback (most recent call last):
      File "timelinelib\wxgui\dialogs\categoryeditor.pyc", line 132, in _btn_ok_on_click
      File "timelinelib\editors\category.pyc", line 55, in save
      File "timelinelib\wxgui\dialogs\categoryeditor.pyc", line 88, in handle_invalid_name
    TypeError: not all arguments converted during string formatting

    Timeline version: 1.4.1
    System version: Windows, nele-notebook, XP, 5.1.2600, x86, x86 Family 6 Model 15 Stepping 13, GenuineIntel
    Python version: 2.7.6 (default, Nov 10 2013, 19:24:18) [MSC v.1500 32 bit (Intel)]
    wxPython version: 2.8.12.1 (msw-unicode)
