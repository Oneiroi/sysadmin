#!/bin/bash

#
# Very quick script to get current swap usage
# David Busby oneiroi@fedoraproject.org
#

ls /proc/ | egrep '[0-9]' | while read pid; do echo "`ps -p $pid -o comm --no-headers` `grep Swap /proc/$pid/smaps | awk '{ x += $2 } END { print x }'`"; done | awk '{ y[$1] += $2 } END { for ( k in y ) { print k, y[k] }}'
