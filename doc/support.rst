Support
=======

Do you need help with timeline? This is where to look.

The manual
----------

The manual that you are reading right now might have the answer to your
question. Browse it to see if you can find it. You can also search this manual.

The mailing list
----------------

We use a mailing list for all kinds of discussions about timeline. Before you
send your question, please :sf:`browse <mailman/thetimelineproj-user>` or
:sf:`search <mailman/search/?mail_list=thetimelineproj-user>` the mailing
archive to see if you can find your answer.

If you can't find your answer, send an email to
thetimelineproj-user@lists.sourceforge.net.

FAQ
---

Can't zoom wider than 1200 years
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Timeline should not be able to zoom wider than 1200 years. But unfortunately,
this happens sometimes, and a period larger than 1200 years gets written to the
``.timeline`` file.

When this happens, you can no longer open the file.

This is a bug in timeline that we should fix. But there is a workaround that
you can use to fix the problem yourself.

The ``.timeline`` file is actually just an xml file. In there, somewhere around
the bottom of the file, you should find this section::

    <displayed_period>
      <start>2013-09-28 00:10:06</start>
      <end>2013-10-09 20:34:55</end>
    </displayed_period>

If you open the ``.timeline`` file in a text editor and change the start and
end dates to be a period less than 1200 years, you should be able to open your
file again.

Make sure that you save the file with UTF-8 encoding.
