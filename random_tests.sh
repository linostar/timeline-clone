#!/bin/sh

set -e

while true; do
    ./execute-specs.py --only specs.Event. specs.Category.
done
