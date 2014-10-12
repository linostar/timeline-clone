#!/bin/sh

set -e

while true; do
    ./execute-specs.py --only test_can_be_compared test_can_be_cloned specs.Undo.
done
