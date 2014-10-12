#!/bin/sh

set -e

while true; do
    ./execute-specs.py --only \
        specs.Event.describe_event \
        specs.SubeventObject.describe_subevent \
        specs.ContainerObject.describe_container \
        specs.TimePeriod.time_period_spec \
        specs.Category.describe_category
done
