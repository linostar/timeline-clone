#!/bin/sh
~/.cabal/bin/codemonitor <<EOF
.
tests \.py$ python execute-specs.py --skip-gui
EOF
