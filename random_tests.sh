#!/bin/sh

set -e

while true; do
    ./execute-specs.py --only \
        specs.Event.describe_event_fundamentals \
        specs.SubeventObject.describe_subevent_fundamentals \
        specs.Category.describe_category_fundamentals
done
