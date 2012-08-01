#!/bin/bash

#
# Quickly and cheaply get a file count and total file size of directory contents.
# Author: David Busby oneiroi@fedoraproject.org http://blog.oneiroi.co.uk
# Changes:
#     v1.0 12 Jul 2012 Initial Release.
#

[[ -z "$1" ]]  && echo "Usage: $0 /folder/to/check" && exit 1

ls $1 | while read dname; do echo -ne "$dname\tis\t"; find $1/${dname} -type f -printf "%s\n" | awk '{ x += $1; y += 1 } END { print y"\tfiles\t" x/1024/1024/1024 " GB" }'; done
