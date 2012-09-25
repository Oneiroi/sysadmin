#!/bin/bash

unset PYTHONPATH
unset PYTHONHOME

while getopts "a:b:u:p:s" opt; do
    case "$opt" in
        a) A=$OPTARG;;
        b) B=$OPTARG;;
        u) U=$OPTARG;;
        p) P=$OPTARG;;
        [?]) echo "Invalid option $opt" && exit 2;;
    esac
done
#added -l 1000 -w 500 25/06/2012
/usr/bin/python /usr/local/zenoss/common/libexec/check_mysql_replication.py -a $A -b $B -u $U -p $P -l 1000 -w 500
check_code=$?

[[ $check_code -eq 0 ]] && exit $check_code;
[[ $check_code -eq 1 ]] && echo -n '| Severity=Warning' && exit $check_code;
[[ $check_code -eq 2 ]] && echo -n '| Severity=Critical' && exit $check_code;
