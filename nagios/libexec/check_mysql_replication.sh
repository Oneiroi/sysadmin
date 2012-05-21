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

/usr/local/zenoss/common/libexec/check_mysql_replication.py -a $A -b $B -u $U -p $P
exit $?
