Installing
==========

Timeline runs on multiple platforms. If you can run `Python
<http://www.python.org/>`_ and `wxPython <http://www.wxpython.org/>`_ you
should be able to run Timeline. However, timeline is only tested on Windows and
Linux.

The recommended way to install timeline is with a binary package or installer.
If that is not available for your platform, you have to install from source.

If you have problems installing timeline, please see the :doc:`support` page
for ways to get help.

Installing with a binary package or installer
---------------------------------------------

Windows
^^^^^^^

.. image:: /images/logo-windows.png
    :align: right

We provide a binary installer for Windows. It installs an executable version of
timeline built with `py2exe <http://www.py2exe.org/>`_. It is a self contained
executable that doesn't need any other dependencies.

Download |latest_exe|_ and execute it.
(:sfl:`Other downloads <files/thetimelineproj>`.)

Fedora
^^^^^^

.. image:: /images/logo-fedora.png
    :align: right

Someone else has packaged timeline for Fedora. Install using::

    su -c 'yum install timeline'

Note that the version included in Fedora is often not the latest.

.. _label-installing-from-source:

Installing from source
----------------------

.. image:: /images/logo-source.png
    :align: right

Get the source code here: |latest_zip|_.
(:sfl:`Other downloads <files/thetimelineproj>`.)

When you install from source, you have to install all required dependencies
yourself. Timeline requires:

* Python version 2.5 or greater (http://www.python.org)
* wxPython version 2.8.9.2 or greater (http://www.wxpython.org)

On Linux systems, you can often install these via the package manager.

Once you have extracted the timeline zip and installed the required
dependencies, you should be able to run the application with this command::

    python <path-to-timeline-directory>/source/timeline.py

Preferable you create a shortcut on your platform that issues this command.
