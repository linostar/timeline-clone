Release instructions
====================

Feature freeze
--------------

When all features for a major version (x.y) have been implemented in main we
move the development for that version over to stable. In stable we prepare for
the (x.y.0) release and then continue to do bugfix releases (x.y.1, x.y.2, ..)
there.

Features for the next version (x.y+1) can continue to be developed in main.

1. Move main repo to stable repo
    1. ``cd stable``
    2. ``hg pull ../main``
    3. ``hg push``
2. Change versions numbers in main to denote the next version (x.y+1.0)
    1. timelinelib/meta/version.py
    2. doc/changelog.rst
    3. Run ``python execute-specs.py`` to find where else you need to modify
3. Commit and push

Work on stable
--------------

1. Fix bugs
2. Import translations from Launchpad
    1. Request download from here (login required)
       http://translations.launchpad.net/thetimelineproj/trunk/+translations
    2. Run ``python import-po-from-launchpad-export.py /path/to/launchpad-export.tar.gz``
    3. Upload new pot-file (Create new po-file with the command ``scons pot``)
3. Check that information and version numbers are correct in
    1. timelinelib/meta/version.py
    2. doc/changelog.rst
4. Run ``python execute-specs.py`` to find possible errors

Last changes on stable
----------------------

1. Update timelinelib/meta/version.py so that DEV=False
    1. Commit
2. Run ``python release/make-source-release.py``
3. Try running the unzipped release to make a basic check that it works
4. Run ``hg tag x.y.z``

After
-----

* Upload source release to SourceForge
* Create binary packages and upload to SourceForge
* Make release announcement with ``python release/release-announcer.py``
