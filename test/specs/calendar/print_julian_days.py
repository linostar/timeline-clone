import sys
import os.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import timelinelib.calendar.gregorian as gregorian

if __name__ == "__main__":
    for julian_day in range(10000000):
        (year, month, day) = gregorian.from_julian_day(julian_day)
        roundtrip_julian_day = gregorian.to_julian_day(year, month, day)
        print("%d - %d-%d-%d - %d" % (julian_day, year, month, day, roundtrip_julian_day))
