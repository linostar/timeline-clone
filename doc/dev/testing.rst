Testing timeline
================

Automated tests (unit tests)
----------------------------

We like automated test. All of timeline's automated tests can be run with a
single command::

    ./execute-specs.py

If you are working on a specific feature and only want to run a subset of the
tests, you can do it like this::

    ./execute-specs.py --only specs.Event. specs.Category.

Some of tests have a bit of randomness to them. So running them multiple times
might give different results. We have a script to run the tests a number of
times in sequence::

    ./execute-specs-repeat.py

It works for a subset as well::

    ./execute-specs-repeat.py --only specs.Event. specs.Category.

Translations
------------

To test translations, you need:

* SCons (http://www.scons.org/)
* gettext (http://www.gnu.org/software/gettext/)
    * Windows users: get the zipfiles gettext-tools-0.17.zip and
      gettext-runtime-0.17-1.zip from here
      http://ftp.acc.umu.se/pub/gnome/binaries/win32/dependencies/.

Test with::

    scons mo
    LANG=sv_SE ./timeline.py
