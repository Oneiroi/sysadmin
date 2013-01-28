#!/bin/bash

#
# Very quick script to get current swap usage
# Author: David Busby oneiroi@fedoraproject.org http://blog.oneiroi.co.uk
# Changes:
#    v1.0 01 Aug 2012 Initial Release
#    v1.1 28 Jan 2013 renamed getswap.sh to interogate_smaps.sh provides full summary of snmaps kbytes


smaps_summary(){
  if [ -f "/proc/$1/smaps" ]; then
    /usr/bin/cat /proc/$1/smaps |\
    egrep 'Size|Rss|Pss|Shared_|Private|Reference|Anon|Swap|Kernel|MMU|Locked' | /usr/bin/sort -k1 |\
    awk '{x[$1] += $2} END { for ( k in x ) { printf "%s %s\t",k,x[k]}}'
    echo ""
  else
    echo "NO SMAPS FILE";
  fi
}

ls /proc/ | egrep '[0-9]' | \
while read pid; do \
  echo -n "`ps -p $pid -o comm --no-headers`  ";
  smaps_summary $pid
done
