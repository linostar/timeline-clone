#!/bin/sh

USERNAME="rickardlindberg"

HOST="$USERNAME,thetimelineproj@web.sourceforge.net"
ROOT=/home/project-web/thetimelineproj
RSYNC_FLAGS="--recursive --del --progress"

make html && rsync $RSYNC_FLAGS _build/html/ $HOST:$ROOT/htdocs
