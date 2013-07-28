#!/bin/sh

set -a

cd $(dirname $0)

rm -f julian_days.c.txt
rm -f julian_days.py.txt
rm -f print_julian_days

python print_julian_days.py > julian_days.py.txt
gcc print_julian_days.c -o print_julian_days && ./print_julian_days > julian_days.c.txt
diff julian_days.py.txt julian_days.c.txt && echo OK
