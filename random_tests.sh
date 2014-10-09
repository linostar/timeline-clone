#!/bin/sh

set -e

while true; do
    ./execute-specs.py --only \
        specs.Event.describe_event \
        specs.SubeventObject.describe_subevent \
        specs.Category.describe_category
done
