Class descriptions
==================

This page explains how some of the classes in timeline works.

GUI classes
-----------

.. image:: /images/classes-gui-overview.png

Drawing
-------

.. image:: /images/classes-drawing.png

For the purpose of making testing easier we try to divide gui-components in two
parts: the GUI class itself and another class, the controller, containing the
'business' logic. The goal is to have no 'business' logic at all in the GUI
class. It should only have simple gui actions.

Another design decision for the purpose of making testing easier is to inject
objects into the constructor of a class. This can be seen here when the
``DrawingArePanel`` creates its controller, the ``DrawingArea``, it passes the
drawer object in the constructor, ``get_drawer()``.

Database
--------

.. image:: /images/classes-database.png

================ ===========================================================
Class            Description
================ ===========================================================
IcsTimleine      Data read from an ics file. The Timeline becomes read-only.
DirTimeline      Data read from the filesystem and displays directories and
                 files in a timeline. The Timeline becomes read-only.
XmlTimeline      Data read from an xml file.
TutorialTimeline The tutorial timeline is not a class by itself. It's a
                 MemoryDb filled with fixed data by the function.
                 ``create_in_memory_tutorial_db()``.
MemoryDb         The base class for Timeline classes that are not read-only.
================ ===========================================================

Startup
-------


.. image:: /images/classes-startup.png
