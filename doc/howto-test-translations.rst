Test translations
=================

To test translations, you need:

* SCons (http://www.scons.org/)
* gettext (http://www.gnu.org/software/gettext/)
    * Windows users: get the zipfiles gettext-tools-0.17.zip and
      gettext-runtime-0.17-1.zip from here
      http://ftp.acc.umu.se/pub/gnome/binaries/win32/dependencies/.

Test with::

    scons mo
    LANG=sv_SE ./timeline.py
