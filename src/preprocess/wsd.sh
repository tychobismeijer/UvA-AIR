#!/bin/bash
LOC=""
for f in $*; do
    g=`basename $f -pp`
    if grep -qFe $g "done-wsd"; then
        echo "SKIP $g";
    elif python3 "$LOC/wsd_bag.py" $f > "$g-wsd"; then
        echo "DONE $g"
        echo "$g" >> "done-wsd"
    fi
done;
