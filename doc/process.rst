Process
=======

This page describes how changes to timeline are made.

It describes how we work.

If we find better ways of working we can change this process to reflect that.

General workflow
----------------

* We continuously collect problems to be included in the backlog
* We work in sprints that are around 3 months long
* In each sprint we work on items from the backlog with highest priority
* At the end of each sprint a new release is made

Backlog
-------

The backlog contains problems that have been identified by users of timeline.

Collecting problems
~~~~~~~~~~~~~~~~~~~

* The main way users of timeline interact with the project is via the mailing list
* Requests that users make are transformed into problem descriptions
* Usually a conversation is needed to find the problem description
* Crash reports are already clear problem descriptions
* Problems are stored in the backlog

Prioritization
~~~~~~~~~~~~~~

* A problem is prioritized higher if more users have experienced it
* Anyone is allowed to comment on problems in the backlog to indicate its
  importance to them

Sprints
-------

* A developer picks a problem from the backlog (preferably a problem with high
  priority) and works on it
* To be accepted for inclusion in timeline, each patch must
    * follow guidelines
    * pass tests
* A patch is delivered by pushing to the repo (if the developer has
  push-access)
* A patch is delivered by sending it to the mailing list (if the developer
  lacks push-access)

Release
-------

* At the end of a sprint a developer creates release packages and uploads to
  SourceForge
