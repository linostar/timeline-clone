#!/bin/sh
hg revert --all && hg clean --all && ctags --python-kinds=-i --extra=+f -R timelinelib/ specs/
