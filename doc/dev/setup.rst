Setting up a development environment
====================================

The first step in setting up a development environment is to install timeline
from source. Follow the instructions in :ref:`label-installing-from-source`,
but instead of downloading the zip file, get the source code from our
`Mercurial <http://mercurial.selenic.com>`_ repository::

    hg clone http://hg.code.sf.net/p/thetimelineproj/main

Then make sure you can run all tests::

    ./execute-specs.py

If that works, you have the basic environment set up.

Testing translations
--------------------

To test translations, you need:

* SCons (http://www.scons.org/)
* gettext (http://www.gnu.org/software/gettext/)
    * Windows users: get the zipfiles gettext-tools-0.17.zip and
      gettext-runtime-0.17-1.zip from here
      http://ftp.acc.umu.se/pub/gnome/binaries/win32/dependencies/.

Test with::

    scons mo
    LANG=sv_SE ./timeline.py
