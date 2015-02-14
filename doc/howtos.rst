Howtos
======

Setting up a development environment
------------------------------------

The first step in setting up a development environment is to install timeline
from source. Follow the instructions in :ref:`label-installing-from-source`,
but instead of downloading the zip file, get the source code from our
`Mercurial <http://mercurial.selenic.com>`_ repository::

    hg clone http://hg.code.sf.net/p/thetimelineproj/main

Then make sure you can run all tests::

    ./execute-specs.py

If that works, you have the basic environment set up.
